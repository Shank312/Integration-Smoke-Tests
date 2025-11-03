Integration + Smoke Tests (Chatbot → RAG → LLM Agent)

This repo shows a complete end-to-end pipeline where all 3 main components of an AI system are wired together:
Chatbot  →  RAG Retrieval System  →  LLM Agent  → Eval Metrics

When you send a /chat request → the full chain executes → and we validate the output.
This repo also includes a smoke test that asserts:
-response is non-empty
-evaluation metrics in results.json satisfy thresholds
This is how real production AI systems guarantee that pipelines are healthy before deployment.

Folder Structure
| folder / file                     | purpose                                          |
| --------------------------------- | ------------------------------------------------ |
| `/chatbot`                        | frontend/backend chatbot components              |
| `/rag-system`                     | retrieval / context fetch (RAG) code             |
| `/llm-agent`                      | agent logic + LLM call                           |
| `app.py`                          | glue layer server that wires everything together |
| `/integration_tests/e2e_smoke.py` | the smoke test                                   |
| `results.json`                    | output metrics written after each request        |

How to run server
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r rag-system/requirements.txt  # if present
pip install flask requests pytest
python app.py

Server will start at:
http://127.0.0.1:5000

Test the pipeline manually
$body = @{
  message = "Wire chatbot → rag-system → llm-agent using prompt layer. Summarize in one sentence."
  metadata = @{ tags = @("e2e","smoke") }
  stream = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:5000/chat" -Method Post -ContentType "application/json" -Body $body

Run smoke test
$env:BASE_URL="http://127.0.0.1:5000"
$env:CHAT_PATH="/chat"
$env:RESULTS_JSON_PATH="./results.json"
$env:EVAL_THRESHOLDS='{"overall.score":0.6,"faithfulness":0.7}'

pytest -q integration_tests/e2e_smoke.py

If thresholds are met → ✅ PASS.

If not → ❌ FAIL and pipeline needs fixing.


Why this matters
This is not “just a model test”.
This is system verification.
In professional AI products:
integration + smoke testing is required before pushing code in production.


Next steps (planned)
replace stub logic with real vector DB + real LLM client
add CI pipeline (GitHub Actions) that blocks PR if smoke test fails
publish as template to use in ANY AI project

Author
Shankar Kumar (Shank312)

If you like this design, star ⭐ the repo & feel free to clone/fork.
