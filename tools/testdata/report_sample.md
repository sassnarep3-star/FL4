<!--
PARSER TEST FIXTURE - not project data.
Format replica of the official report page as returned by the page reader, using a handful of
rows already published in data/injuries_week10_2026.json. Its only purpose is to let
tools/fetch_injuries.py be tested for format handling without re-fetching the live page.
Expected result of running the parser on this file: 15 rows read, 5 kept (WAS 2, NE 1, DET 2);
Questionable and blank-status rows dropped; teams mapped from the logo lines. Verified 2026-11-14:
`python3 tools/fetch_injuries.py --raw tools/testdata/report_sample.md -o /tmp/parsed.json`
returns exactly that, and WAS out=2 matches data/injuries_week10_2026.json.
-->

# 2026 NFL Injury Report

## THURSDAY, NOVEMBER 12TH

8:15 PMEST

Prime Video

[![](https://static.www.nfl.com/t_q-best/league/api/clubs/logos/WAS)](https://www.nfl.com/teams/washington-commanders/) WAS [Commanders](https://www.nfl.com/teams/washington-commanders/)

(3-5-1)

[![](https://static.www.nfl.com/t_q-best/league/api/clubs/logos/NYG)](https://www.nfl.com/teams/new-york-giants/) NYG [Giants](https://www.nfl.com/teams/new-york-giants/)

(5-3-1)

Commanders

| Player | Position | Injuries | Practice Status | Game Status |
| --- | --- | --- | --- | --- |
| [John Bates](https://www.nfl.com/players/john-bates/) | TE |  | Full Participation in Practice |  |
| [Jayden Daniels](https://www.nfl.com/players/jayden-daniels/) | QB |  | Full Participation in Practice |  |
| [Lucas Patrick](https://www.nfl.com/players/lucas-patrick/) | C | Concussion | Did Not Participate In Practice | Out |
| [Amik Robertson](https://www.nfl.com/players/amik-robertson/) | CB |  | Limited Participation in Practice |  |
| [Colson Yankoff](https://www.nfl.com/players/colson-yankoff/) | TE | Knee | Did Not Participate In Practice | Out |

Giants

| Player | Position | Injuries | Practice Status | Game Status |
| --- | --- | --- | --- | --- |
| [Abdul Carter](https://www.nfl.com/players/abdul-carter/) | LB |  | Full Participation in Practice |  |
| [Malik Harrison](https://www.nfl.com/players/malik-harrison/) | LB | Groin | Limited Participation in Practice | Questionable |
| [Theo Johnson](https://www.nfl.com/players/theo-johnson/) | TE |  | Full Participation in Practice |  |

## SUNDAY, NOVEMBER 15TH

9:30 AMEST

FOX, FOX DEPORTES

[![](https://static.www.nfl.com/t_q-best/league/api/clubs/logos/NE)](https://www.nfl.com/teams/new-england-patriots/) NE [Patriots](https://www.nfl.com/teams/new-england-patriots/)

(5-4)

[![](https://static.www.nfl.com/t_q-best/league/api/clubs/logos/DET)](https://www.nfl.com/teams/detroit-lions/) DET [Lions](https://www.nfl.com/teams/detroit-lions/)

(6-2)

Patriots

| Player | Position | Injuries | Practice Status | Game Status |
| --- | --- | --- | --- | --- |
| [Ben Brown](https://www.nfl.com/players/ben-brown-2/) | C | Knee | Did Not Participate In Practice | Out |
| [A.J. Brown](https://www.nfl.com/players/a-j-brown/) | WR | Ankle, Knee | Limited Participation in Practice | Questionable |
| [Drake Maye](https://www.nfl.com/players/drake-maye/) | QB |  | Full Participation in Practice |  |
| [Walter Rouse](https://www.nfl.com/players/walter-rouse/) | T | Concussion | Limited Participation in Practice | Questionable |

Lions

| Player | Position | Injuries | Practice Status | Game Status |
| --- | --- | --- | --- | --- |
| [Brian Branch](https://www.nfl.com/players/brian-branch/) | S |  | Full Participation in Practice |  |
| [Kerby Joseph](https://www.nfl.com/players/kerby-joseph/) | S | Knee | Did Not Participate In Practice | Out |
| [D.J. Reed](https://www.nfl.com/players/d-j-reed/) | CB | Hip | Did Not Participate In Practice | Out |
