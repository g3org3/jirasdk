import json
import logging
from os import environ

import requests as r

log = logging.getLogger(__name__)


def get_field_from_list(field, objs):
    if not objs:
        return []
    return [o.get(field) for o in objs]


def get_fields_from_list(fields, objs):
    if not objs:
        return []
    return [{field: item.get(field) for field in fields} for item in objs]


def get_fields(fields, obj):
    if not obj:
        return None
    data = {}
    for field in fields:
        data.setdefault(field, obj.get(field))
    return data


def get_from_pr(obj):
    if not obj:
        return []

    return [
        {
            "author": f'{o.get("author").get("name")} ({o.get("author").get("url").split("/")[-1]})',
            "id": o.get("id"),
            "name": o.get("name"),
            "commentCount": o.get("commentCount"),
            "reviewers": get_field_from_list("name", o.get("reviewers")),
            "status": o.get("status"),
            "url": o.get("url"),
            "lastUpdate": o.get("lastUpdate"),
        }
        for o in obj
    ]


class Jira:
    base_url: str
    api_key: str
    verify_ssl: bool
    headers: dict[str, str]

    # fmt:off
    def __init__(self, host: str | None = None, api_key: str | None = None, verify_ssl: bool = True):
    # fmt:on
        _host = host or environ["JIRA_HOST"]
        self.api_key = api_key or environ["JIRA_API_KEY"]
        log.info(
            f"Init jira client (host={_host}, api_key={self.api_key}, verify_ssl={verify_ssl})"
        )
        self.base_url = f"https://{_host}/rest"
        self.verify_ssl = verify_ssl
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    def jira_request(self, method: str, endpoint: str, json=None, params=None):
        url = f"{self.base_url}/{endpoint}"
        log.info(f"{method} {endpoint}", "API")
        res = r.request(
            method,
            url,
            json=json,
            params=params,
            headers=self.headers,
            verify=self.verify_ssl,
        )
        res.raise_for_status()
        log.info(f"{res.status_code} {endpoint}")
        return res.json()

    def jira_request_get_all_pages(self, endpoint: str, params: dict[str, str] = {}):
        startAt = 0
        params["startAt"] = str(startAt)
        payload = self.jira_request("GET", endpoint, params=params)
        items = payload["values"]
        while payload and not payload["isLast"]:
            startAt += 50
            params["startAt"] = str(startAt)
            payload = self.jira_request("GET", endpoint, params=params)
            items += payload["values"]
        return items

    def jira_request_get_all_issues(self, endpoint: str, params: dict[str, str] = {}):
        startAt = 0
        params["startAt"] = str(startAt)
        payload = self.jira_request("GET", endpoint, params=params)
        items = payload["issues"]
        is_last = int(payload["maxResults"]) + int(payload["startAt"]) >= int(
            payload["total"]
        )
        while payload and not is_last:
            startAt += 50
            params["startAt"] = str(startAt)
            payload = self.jira_request("GET", endpoint, params=params)
            items += payload["issues"]
            is_last = int(payload["maxResults"]) + int(payload["startAt"]) >= int(
                payload["total"]
            )
        return items

    def search_jira_tickets(self, jql: str, fields: list[str] = []):
        default_fields = [
            "summary",
            "reporter",
            "description",
            "assignee",
            "labels",
            "status",
        ]
        params = {
            "jql": jql,
            "fields": fields or default_fields,
        }
        log.info(f"jql={jql}")
        log.info(f"fields={','.join(fields or default_fields)}")
        items = self.jira_request_get_all_issues("api/2/search", params=params)
        return items

    def get_all_tickets_from_epic(self, project: str, epic_key: str, include_done_tickets: bool = False):
        log.info(f"get_all_tickets_from_epic({epic_key})")
        status = '"Rejected"' if include_done_tickets else '"Rejected", "Done"'
        tickets = self.search_jira_tickets(
            f'project = {project} AND "Epic Link" = {epic_key}'
            f" AND status not in ({status})"
        )
        return tickets

    def post_comment_in_jira_ticket(self, ticket_key: str, comment: str):
        log.info(f"write_comment_in_jira_ticket({ticket_key})")
        payload = {"body": comment}
        self.jira_request("POST", f"api/2/issue/{ticket_key}/comment", json=payload)

        return "success"

    def get_jira_sprints(self, board_id: str):
        log.info("get_jira_sprints")
        fields = ["id", "state", "name", "goal", "startDate"]

        items = self.jira_request_get_all_pages(
            f"agile/1.0/board/{board_id}/sprint?state=future"
        )
        future_sprints = get_fields_from_list(fields, items)

        items = self.jira_request_get_all_pages(
            f"agile/1.0/board/{board_id}/sprint?state=active"
        )
        active_sprint = get_fields_from_list(fields, items)

        sprints = active_sprint + future_sprints

        return sprints

    def get_jira_ticket(self, ticket_key: str):
        log.info(f"get_jira_ticket({ticket_key})")
        payload = self.jira_request("GET", f"api/2/issue/{ticket_key}")
        fields = payload.get("fields")

        github_desc = json.loads(
            fields.get("customfield_11100").split("devSummaryJson=")[1][0:-1]
        )
        comments = fields.get("comment").get("comments") if fields.get("comment") else []
        sprints = fields.get("customfield_10005") or []

        data = {
            "id": payload.get("id"),
            "key": payload.get("key"),
            "summary": fields.get("summary"),
            "description": fields.get("description"),
            "comments": [
                {
                    "author": get_fields(["name", "displayName"], c.get("author")),
                    "body": c.get("body"),
                    "created": c.get("created"),
                }
                for c in comments
            ],
            "created": fields.get("created"),
            "reporter": get_fields(["name", "displayName"], fields.get("reporter")),
            "assignee": get_fields(["name", "displayName"], fields.get("assignee")),
            "status": get_fields(["id", "name"], fields.get("status")),
            "issuetype": get_fields(["name", "id"], fields.get("issuetype")),
            "labels": fields.get("labels"),
            "sprints": [
                [field for field in s.split(",") if "name=" in field][0] for s in sprints
            ],
            # "issuelinks": fields.get("issuelinks"),
            "github": github_desc.get("cachedValue")
            .get("summary")
            .get("pullrequest")
            .get("overall"),
        }

        return data

    def update_jira_ticket_status(self, ticket_key: str, status_id: int):
        log.info(f"update_jira_ticket_status({ticket_key}, {status_id})")
        payload = {
            "transition": {
                "id": status_id,
            }
        }
        self.jira_request("POST", f"api/2/issue/{ticket_key}/transitions", json=payload)

        return "success"

    def get_jira_ticket_status_list(self, ticket_key: str):
        """
        Gets a list of the available statuses that the ticket can change to.

        Args:
            ticket_key: the jira issue key, it can be something like CFCCON-, PID-, CLPDEF-, IFSDEVOPS-
        """
        log.info(f"get_jira_ticket_status_list({ticket_key})")
        payload = self.jira_request("GET", f"api/2/issue/{ticket_key}/transitions")
        return [
            {"status_id": t.get("id"), "status_name": t.get("name")}
            for t in payload.get("transitions")
        ]

    def assign_user_to_ticket(self, ticket_key: str, user_name: str):
        log.info(f"assign_user_to_ticket({ticket_key}, {user_name})")
        self.jira_request("PUT", f"api/2/issue/{ticket_key}/assignee", {"name": user_name})

    def get_jira_ticket_github_pull_requests(self, issue_id: int):
        log.info(f"get_jira_ticket_github_pull_requests({issue_id})")
        query_string = f"issueId={issue_id}&applicationType=githube&dataType=pullrequest"
        payload = self.jira_request("GET", f"dev-status/1.0/issue/detail?{query_string}")
        payload = payload.get("detail")[0]
        branches = payload.get("branches")
        pullrequests = payload.get("pullRequests")
        data = {
            "branches": get_field_from_list("name", branches),
            "pullRequests": get_from_pr(pullrequests),
        }
        return data

    def get_all_epics(self, board_id: str, show_done_epics: bool = False):
        items = self.jira_request_get_all_pages(
            f"agile/1.0/board/{board_id}/epic", 
            params={"done": str(show_done_epics).lower()},
        )
        return get_fields_from_list(["id", "name", "key"], items)

    def create_jira_ticket(
        self,
        project_id: int,
        summary: str,
        description: str,
        issue_type_id: int,
        sprint_id: int,
        epic_id: int | None = None,
    ):
        log.info(f"create_jira_ticket({summary}, {issue_type_id},{sprint_id})")
        payload = {
            "fields": {
                "project": {
                    "id": project_id,
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "id": issue_type_id,
                },
                "customfield_10005": sprint_id,
            }
        }
        if epic_id:
            payload["fields"]["customfield_10001"] = epic_id
        data = self.jira_request("POST", "api/2/issue", json=payload)
        return data
