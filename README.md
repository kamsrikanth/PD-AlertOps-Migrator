# PD-AlertOps-Migrator
Migrator script for porting users/groups/schedules from PagerDuty to AlertOps

==============================================================================

*****Code is currently in draft mode (working), need to organize it more and migration currently works for users and groups*****



- To run the applicationb UI, make sure you have Python v3.5 or above. 
- To open the application,  run the command in terminal/your editor as - 'python pd_ao_mg.py"

You will need the PagerDuty API Key (v2, with full access) and the AlertOps v2 API Key [REMEMBER this works only with the v2 version of AlertOps)

- On providing the API Keys, you should be able to retrieve the Teams from PagerDuty, you can select multiple teams, or a single team, and the corresponding users in each team will be migrated to AlertOps.

- If no team is available or selected, you will just be migrating the Users from PagerDuty to AlertOps
