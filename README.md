# NYT-Connections-API

A Python-based API that interfaces with The New York Times to fetch and process connection data. This project utilizes Github actions to scrape data to keep the database up to date.

## Endpoints
`/connections`: Fetches the connections puzzle of the day

`/connections/{date}`: Fetches data for a specific connection by date.

<details>
<summary><code>date</code></summary>
<br>
Format: <code>YYYY-MM-DD</code>
</details>

---

View the live API [here](https://nyt-connections.up.railway.app/)
