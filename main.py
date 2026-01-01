import flet as ft
from ollama_client import OllamaClient
from database import init_db, create_session, get_sessions, add_message, get_messages, update_session_title, delete_session
from transcriber import Transcriber
import os
import threading
import uuid

def main(page: ft.Page):
    page.title = "Ollama Chat"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed="indigo")

    # Initialize DB
    init_db()

    # State
    client = OllamaClient()
    # Initialize Transcriber (Singleton)
    # We will initialize it on first use or here. Since it's a singleton now, it's safer.
    transcriber = None

    current_session_id = None
    models = client.list_models()

    # Layout Components
    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        padding=20,
        auto_scroll=True
    )

    def get_initial_model():
        return models[0] if models else "llama3"

    model_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(m) for m in models],
        value=get_initial_model(),
        width=200,
        label="Model"
    )

    prompt_field = ft.TextField(
        hint_text="Type a message...",
        expand=True,
        multiline=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        border_radius=20
    )

    def load_chat_history(session_id):
        nonlocal current_session_id
        current_session_id = session_id
        chat_list.controls.clear()
        messages = get_messages(session_id)
        for msg in messages:
            chat_list.controls.append(create_message_bubble(msg['role'], msg['content']))
        page.update()

    def create_message_bubble(role, content):
        is_user = role == "user"
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Markdown(
                        content,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        code_theme="atom-one-dark",
                        code_style=ft.TextStyle(font_family="monospace"),
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT if not is_user else ft.colors.PRIMARY_CONTAINER,
                    padding=15,
                    border_radius=15,
                    expand=True if not is_user else False,
                    width=None if is_user else 600, # Constrain width for bot somewhat
                )
            ],
            alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def send_message(e):
        nonlocal current_session_id
        user_text = prompt_field.value.strip()
        if not user_text:
            return

        if not current_session_id:
            # Create new session if none exists
            # Use first few words as title
            title = " ".join(user_text.split()[:5])
            current_session_id = create_session(title)
            refresh_sidebar()

        # Add User Message to UI and DB
        prompt_field.value = ""
        prompt_field.focus()

        user_msg_ui = create_message_bubble("user", user_text)
        chat_list.controls.append(user_msg_ui)
        add_message(current_session_id, "user", user_text)
        page.update()

        # Prepare for Bot Response
        bot_response_text = ""
        bot_msg_ui = create_message_bubble("assistant", "...")
        chat_list.controls.append(bot_msg_ui)
        page.update()

        # Streaming Logic
        history = get_messages(current_session_id)
        api_messages = [{'role': m['role'], 'content': m['content']} for m in history]

        # Stream
        try:
            stream = client.chat(model_dropdown.value, api_messages)

            first_chunk = True
            for chunk in stream:
                if first_chunk:
                    bot_response_text = ""
                    first_chunk = False

                bot_response_text += chunk
                # Update UI
                bot_msg_ui.controls[0].content.value = bot_response_text
                page.update()

            # Save complete response to DB
            add_message(current_session_id, "assistant", bot_response_text)

        except Exception as ex:
            bot_msg_ui.controls[0].content.value = f"Error: {str(ex)}"
            page.update()

    # Voice Dictation Logic
    audio_recorder = ft.AudioRecorder()
    page.overlay.append(audio_recorder)
    is_recording = False
    current_audio_path = None

    def toggle_record(e):
        nonlocal is_recording, transcriber, current_audio_path

        if not is_recording:
            # Start Recording
            # Generate unique filename to avoid race conditions
            current_audio_path = f"input_{uuid.uuid4().hex}.wav"

            audio_recorder.start_recording(current_audio_path)
            is_recording = True
            mic_button.icon = ft.icons.STOP_CIRCLE
            mic_button.icon_color = ft.colors.RED
            mic_button.tooltip = "Stop Recording"
            prompt_field.hint_text = "Recording..."
            page.update()
        else:
            # Stop Recording
            result = audio_recorder.stop_recording()
            is_recording = False
            mic_button.icon = ft.icons.MIC
            mic_button.icon_color = None
            mic_button.tooltip = "Dictate"
            prompt_field.hint_text = "Processing audio..."
            prompt_field.disabled = True
            page.update()

            # Transcribe in background thread to not freeze UI
            def process_audio(filepath):
                nonlocal transcriber
                try:
                    if transcriber is None:
                        # Will return existing instance if created
                        transcriber = Transcriber()

                    if filepath and os.path.exists(filepath):
                        text = transcriber.transcribe(filepath)
                        # Clean up file
                        try:
                            os.remove(filepath)
                        except:
                            pass

                        # Update UI from thread
                        prompt_field.value = (prompt_field.value or "") + " " + text
                except Exception as ex:
                    print(f"Transcription error: {ex}")
                finally:
                    prompt_field.disabled = False
                    prompt_field.hint_text = "Type a message..."
                    prompt_field.focus()
                    page.update()

            threading.Thread(target=process_audio, args=(current_audio_path,)).start()

    mic_button = ft.IconButton(
        icon=ft.icons.MIC,
        on_click=toggle_record,
        tooltip="Dictate"
    )

    send_button = ft.IconButton(
        icon=ft.icons.SEND_ROUNDED,
        on_click=send_message,
        icon_color=ft.colors.PRIMARY,
    )

    # Sidebar

    sidebar_content = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    def delete_chat(session_id):
        delete_session(session_id)
        if current_session_id == session_id:
             # Clear view if deleted current
             chat_list.controls.clear()
        refresh_sidebar()

    def refresh_sidebar():
        sessions = get_sessions()
        sidebar_content.controls.clear()

        # New Chat Button
        def new_chat_click(e):
            nonlocal current_session_id
            current_session_id = None
            chat_list.controls.clear()
            page.update()

        sidebar_content.controls.append(
            ft.Container(
                content=ft.Row([ft.Icon(ft.icons.ADD), ft.Text("New Chat")]),
                padding=10,
                on_click=new_chat_click,
                ink=True,
                border_radius=10
            )
        )

        for sess in sessions:
            # Capture variable in closure
            sid = sess['id']
            stitle = sess['title'] or "Untitled"

            # Using a simplified list tile look
            def on_click_handler(e, session_id=sid):
                load_chat_history(session_id)

            sidebar_content.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.CHAT_BUBBLE_OUTLINE, size=16),
                        ft.Text(stitle, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True)
                    ]),
                    padding=10,
                    on_click=on_click_handler,
                    ink=True,
                    border_radius=10,
                    data=sid
                )
            )
        page.update()

    # Initial Setup
    refresh_sidebar()

    # Main layout structure
    page.add(
        ft.Row(
            controls=[
                # Sidebar
                ft.Container(
                    width=250,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    padding=10,
                    content=ft.Column([
                        ft.Text("History", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        ft.Divider(),
                        sidebar_content
                    ])
                ),
                # Main Chat Area
                ft.Column(
                    expand=True,
                    controls=[
                        # Header
                        ft.Container(
                            padding=10,
                            content=ft.Row([
                                ft.Text("Ollama Chat", style=ft.TextThemeStyle.HEADLINE_SMALL),
                                ft.Container(expand=True),
                                model_dropdown
                            ])
                        ),
                        # Messages
                        ft.Container(
                            expand=True,
                            content=chat_list,
                            bgcolor=ft.colors.BACKGROUND
                        ),
                        # Input Area
                        ft.Container(
                            padding=20,
                            content=ft.Row([
                                prompt_field,
                                mic_button,
                                send_button
                            ])
                        )
                    ]
                )
            ],
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
