# jirasdk

## install

```sh
pip install git+https://github.com/g3org3/jirasdk.git --force
```

## Pre-requisites

```sh
# add this to your ~/.zshrc
export JIRA_API_KEY=
export JIRA_HOST=
```

## Getting started

```sh
usage: jira [-h] {search,get-epic-tickets,comment,get-sprints,get-ticket,update-status,get-status-list,assign,get-prs,get-epics,create-ticket} ...

Jira CLI tool

positional arguments:
  {search,get-epic-tickets,comment,get-sprints,get-ticket,update-status,get-status-list,assign,get-prs,get-epics,create-ticket}
                        Available commands
    search              Search Jira tickets using JQL
    get-epic-tickets    Get all tickets from an epic
    comment             Post a comment on a ticket
    get-sprints         Get sprints for a board
    get-ticket          Get a Jira ticket
    update-status       Update ticket status
    get-status-list     Get available statuses for a ticket
    assign              Assign user to ticket
    get-prs             Get GitHub pull requests for a ticket
    get-epics           Get all epics for a board
    create-ticket       Create a new Jira ticket

options:
  -h, --help            show this help message and exit
```
