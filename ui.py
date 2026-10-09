from nicegui import ui
import requests

API_URL = "http://localhost:8005"

questions = []
ui.query("body").style("background-color: #eef2f3;")
page_body = ui.column().classes("w-full max-w-7xl mx-auto items-center gap-6 px-6 py-8")

def api_get(path):
    try:
        # Attempt to send GET request to API
        response = requests.get(f"{API_URL}{path}", timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, GET was successful so return response data
        return response.json()
    except requests.RequestException as e:
        # GET request was unsuccessful
        # Send an alert with error details to the UI and return empty list
        ui.notify(f"Could not reach API: {e}", type="negative")
        return []

def api_post(path, data):
    try:
        # Attempt to send POST request to API with data payload
        response = requests.post(f"{API_URL}{path}", json=data, timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, POST was successful so return True
        return True
    except requests.RequestException as e:
        # POST request was unsuccessful
        # Send an alert with error details to the UI and return False
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False

# TODO: Create api_delete function that attempts to send a DELETE request to the API.
# The request method should use the string f"{API_URL}{path}/{id}" to access the correct path,
# where id refers to the id number of the question to be deleted. 
def api_delete(path, id):
    try:
        response = requests.delete(f"{API_URL}{path}/{id}", timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False

# TODO: Create api_put function that attempts to send a PUT request to the API.
# The request method should use the string f"{API_URL}{path}/{id}" to access the correct path,
# where id refers to the id number of the question to be deleted. The data passed as an argument
# to this function must be sent with the request so that the API knows the updated values to add 
# to the dataset (similar to how data is sent in api_post).
def api_put(path, id, data):
    try:
        response = requests.put(f"{API_URL}{path}/{id}", json=data, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False

def update_question(dialog, question_id, new_q, new_a):
    dialog.close()
    if api_put("/update", question_id, {
        "question": new_q.value,
        "answer": new_a.value,
    }):
        render_page()

def open_edit_dialog(question):
    with ui.dialog() as dialog:
        with ui.card().classes("w-[600px] max-w-[90vw]"):
            new_q = ui.textarea("Question", value=question["q"]).props('rows=4 label-color="orange"').classes("w-full")
            new_a = ui.textarea("Answer", value=question["a"]).props('rows=4 label-color="green"').classes("w-full")
            update_button = ui.button(
                "Update question",
                on_click=lambda: update_question(dialog, question["id"], new_q, new_a),
            )
            update_button.classes("self-center")
    dialog.open()

# TODO: Add edit and delete buttons dynamically to each question card.
def render_question(question):
    with ui.card().classes("w-full max-w-2xl h-44 rounded-xl border border-sky-100 bg-sky-50 p-5 shadow-sm transition-shadow hover:shadow-md cursor-pointer") as card:
        card.on("click", lambda: toggle_answer(question["id"]))
        ui.label(question["q"]).classes("w-full flex-1 flex items-center justify-center text-center text-lg font-semibold text-slate-800")
        ui.label(question["a"]).classes("w-full rounded-md bg-emerald-50 px-3 py-2 text-center text-sm font-bold text-emerald-700").bind_visibility_from(question["state"], "show_answer") 
        with ui.row().classes("relative w-full mt-auto"):
            edit_button = ui.button("Edit", color="blue-10").classes("absolute left-1/2 -translate-x-1/2")
            edit_button.on(
                "click",
                lambda: open_edit_dialog(question),
                js_handler="(event) => { event.stopPropagation(); emit(event); }",
            )

            delete_button = ui.button(text="Delete", color="negative").classes("ml-auto")
            delete_button.on(
                "click",
                lambda: delete_question(question["id"]),
                js_handler="(event) => { event.stopPropagation(); emit(event); }",
            )
def toggle_answer(i):
    question = next(question for question in questions if question["id"] == i)
    question["state"]["show_answer"] = not question["state"]["show_answer"]

def add_new_question(question, answer):
    api_post("/add", {"question": question, "answer": answer})
    render_page()

def delete_question(id):
    if api_delete("/delete", id):
        render_page()

def render_text_inputs():
    with ui.column().classes("w-full items-center"):
        new_question_input = ui.input(label="New question").props("clearable").classes("w-full")
        new_answer_input = ui.input(label="New answer").props('clearable label-color="green-8"').classes("w-full")
        add_question_btn = ui.button(text="Add question", color="positive", on_click=lambda: add_new_question(
            question=new_question_input.value,
            answer=new_answer_input.value
        ))

def init_page():
    render_page()

def render_page():
    global questions
    questions = api_get("/questions")
    page_body.clear()
    with page_body:
        ui.label("HCI Questions").classes("text-3xl font-bold text-slate-800")
        ui.label("Click a question to reveal its answer").classes("rounded-full bg-white px-4 py-2 text-sm font-medium text-slate-500 shadow-sm")
        with ui.row().classes("w-full items-stretch gap-12"):
            with ui.column().classes("flex-1 items-end"):
                for question in questions:
                    question["state"] = {"show_answer": False}
                    render_question(question)
            with ui.column().classes("flex-1 items-center justify-center"):
                with ui.card().classes("w-80 rounded-xl border border-slate-200 bg-white p-6 shadow-md"):
                    render_text_inputs()
    

init_page()
ui.run(port=8084, title="HCI Questions Application")