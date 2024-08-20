# NYT-Connections-API

A Python-based API that interfaces with The New York Times to fetch and process connection data. This project utilizes Github actions to scrape data to keep the database up to date.

## Endpoints
| Endpoint | Type | Description |
| --------- | ------ | ---------|
| `/connections`: | `GET` | Returns the connections puzzle of the day |
| `/{date}`: | `GET` | Returns data for a specific connection by date. |
| `/{date}`: | `GET` | Returns data for a specific connection by date. |
| `/{date}/words` | `GET` | Returns the 16 words. |
| `/{date}/categories` | `GET` | Returns the 4 categories. |
| `/{date}/categories/complete` | `GET` | Returns the 4 categories and their words. |
| `/{date}/categories/{level}` | `GET` | Returns the specific category by level. |
| `/{date}/categories/{level/words}` | `GET` | Returns the words in a specific category by level. |
| `/{date}/guess` | `POST` | Returns the category of the puzzle if correctly guessed with words |
| `/{date}/hint` | `POST` | Returns a hint about a specific category |

<details>
<summary><code>date</code></summary>
<br>
Format: <code>YYYY-MM-DD</code>
</details>

---

View the live API [here](https://nyt-connections.up.railway.app/)
