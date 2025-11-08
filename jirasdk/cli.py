import argparse
import urllib3

from jirasdk import Jira

urllib3.disable_warnings()

def main():
    parser = argparse.ArgumentParser(description="Jira CLI tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # search
    search_parser = subparsers.add_parser(
        "search", help="Search Jira tickets using JQL"
    )
    search_parser.add_argument("jql", help="JQL query string")

    # get-epic-tickets
    epic_parser = subparsers.add_parser(
        "get-epic-tickets", help="Get all tickets from an epic"
    )
    epic_parser.add_argument("project_id", help="Project ID")
    epic_parser.add_argument("epic_key", help="Epic key")

    # comment
    comment_parser = subparsers.add_parser("comment", help="Post a comment on a ticket")
    comment_parser.add_argument("ticket_key", help="Ticket key")
    comment_parser.add_argument("comment", help="Comment text")

    # get-sprints
    sprints_parser = subparsers.add_parser(
        "get-sprints", help="Get sprints for a board"
    )
    sprints_parser.add_argument("board_id", help="Board ID")

    # get-ticket
    ticket_parser = subparsers.add_parser("get-ticket", help="Get a Jira ticket")
    ticket_parser.add_argument("ticket_key", help="Ticket key")

    # update-status
    status_parser = subparsers.add_parser("update-status", help="Update ticket status")
    status_parser.add_argument("ticket_key", help="Ticket key")
    status_parser.add_argument("status", help="New status")

    # get-status-list
    status_list_parser = subparsers.add_parser(
        "get-status-list", help="Get available statuses for a ticket"
    )
    status_list_parser.add_argument("ticket_key", help="Ticket key")

    # assign
    assign_parser = subparsers.add_parser("assign", help="Assign user to ticket")
    assign_parser.add_argument("ticket_key", help="Ticket key")
    assign_parser.add_argument("username", help="Username to assign")

    # get-prs
    pr_parser = subparsers.add_parser(
        "get-prs", help="Get GitHub pull requests for a ticket"
    )
    pr_parser.add_argument("ticket_key", help="Ticket key")

    # get-epics
    epics_parser = subparsers.add_parser("get-epics", help="Get all epics for a board")
    epics_parser.add_argument("board_id", help="Board ID")

    # create-ticket
    subparsers.add_parser("create-ticket", help="Create a new Jira ticket")

    args = parser.parse_args()

    jira = Jira(verify_ssl=False)

    if args.command == "search":
        jira.search_jira_tickets(args.jql)
    elif args.command == "get-epic-tickets":
        jira.get_all_tickets_from_epic(args.project_id, args.epic_key)
    elif args.command == "comment":
        jira.post_comment_in_jira_ticket(args.ticket_key, args.comment)
    elif args.command == "get-sprints":
        sprints = jira.get_jira_sprints(args.board_id)
        print("\nSprints")
        for sprint in sprints:
            print(sprint)
    elif args.command == "get-ticket":
        jira.get_jira_ticket(args.ticket_key)
    elif args.command == "update-status":
        jira.update_jira_ticket_status(args.ticket_key, args.status)
    elif args.command == "get-status-list":
        jira.get_jira_ticket_status_list(args.ticket_key)
    elif args.command == "assign":
        jira.assign_user_to_ticket(args.ticket_key, args.username)
    elif args.command == "get-prs":
        jira.get_jira_ticket_github_pull_requests(args.ticket_key)
    elif args.command == "get-epics":
        jira.get_all_epics(args.board_id)
    elif args.command == "create-ticket":
        print("todo")
        # jira.create_jira_ticket()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
