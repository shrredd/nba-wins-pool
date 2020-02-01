# NBA Wins Pool
Back in 2012, Bill Simmons came up with the idea for an NFL Wins Pool. Check out Bill's [article](https://grantland.com/the-triangle/you-should-have-an-nfl-wins-pool/) for the basic idea. My friend [John](https://www.linkedin.com/in/john-jessen-8a2b601a/) and I wanted to make this happen for the NBA. John made an iPhone app. This repository is the draft order logic that it pulls from.

![Wins Pool Leaderboard](https://github.com/shrredd/nba-wins-pool/raw/master/nba_wins_pool/static/pool-leaderboard.png "Wins Pool Leaderboard")


# Rough API
```
/user/create
  Params:
    -> name (String)
  Returns:
    -> user_id (String)

/pool/size
  Returns:
    -> json.write('2', '3', '5', '6')

/pool/create
  Params:
    -> creator_id (Int)
    -> pool_size (Int)
    -> pool_name (String)
  Returns:
    -> pool_id (String)

/pool/status
  Returns:
    -> pool_status (Dict):
      {
        1 :
        [
          user: {id: "abc12324", name: "Jason Smith"},
          team (None if not drafted yet): {id: "atlanta-hawks", name: "Atlanta Hawks"} or None)
         ],
        2 :
        [
          user: {id: "xasarf3212", name: "Eric Smith"},
          team (None if not drafted yet): {id: "boston-celtics", name: "Boston Celtics"} or None)
         ]
         ...
      }

/pool/join
  Params:
    -> user_id (String)
    -> pool_id (String)
  Returns:
    -> success (Bool)

/pool/select
  Params:
    -> user_id (String)
    -> team_id (String)
  Returns:
    -> pool_status (Dict):
      {
        1 :
        [
          user: {id: "abc12324", name: "Jason Smith"},
          team (None if not drafted yet): {id: "atlanta-hawks", name: "Atlanta Hawks"} or None)
         ],
        2 :
        [
          user: {id: "xasarf3212", name: "Eric Smith"},
          team (None if not drafted yet): {id: "boston-celtics", name: "Boston Celtics"} or None)
         ]
         ...
      }

```
