# made by m and HHS_kt

import os
import sys
import base64
import shutil
import webbrowser
import threading
from pydub import AudioSegment
import FreeSimpleGUIQt as sg

vb_path = ""
output_path = ""
error = False
finished = False


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def unpack():
    if not vb_path.strip():
        raise Exception("You should fill voice.d path")
    if not output_path.strip():
        raise Exception("You should fill output path")

    path = os.path.dirname(vb_path)
    wav_path = output_path + "/wav"

    if not should_merge and not os.path.exists(wav_path):
        os.makedirs(wav_path)

    with open(path + "/inf.d", "r") as f:
        lines = list(
            map(lambda line: base64.b64decode(line).decode("utf-8"), f.readlines())
        )

    with open(output_path + "/reclist.txt", "w") as f:
        f.writelines(map(lambda line: line.split()[0] + "\n", lines[2:]))

    merged_sound = AudioSegment.empty()

    with open(path + "/voice.d", "rb") as f:
        for line in lines[2:]:
            arr = line.split()
            sound = AudioSegment(
                data=f.read(int(arr[2])), sample_width=2, frame_rate=44100, channels=1
            )
            if should_merge:
                merged_sound += sound
            else:
                sound.export(wav_path + "/" + arr[0] + ".wav", format="wav")
                with open(wav_path + "/" + arr[0] + ".inf", "w") as out_f:
                    out_f.write(
                        f"0 {int(arr[2]) // 2} {arr[3]} {arr[4]} {arr[5]} {arr[6]} {arr[7]}"
                    )

    if should_merge:
        merged_sound.set_channels(1)
        merged_sound.set_frame_rate(44100)
        merged_sound.export(output_path + "/merged.wav", format="wav")

    if os.path.exists(path + "/charactor.txt"):
        shutil.copy(path + "/charactor.txt", output_path)

    if os.path.exists(path + "/head.d"):
        shutil.copy(path + "/head.d", output_path + "/head.png")


def unpack_gui():
    global finished, error, output_message
    try:
        unpack()
        output_message = "finished!"
        finished = True
    except Exception as err:

        if hasattr(err, "message"):
            output_message = err.message
        else:
            output_message = str(err)

        error = True


sg.theme("Dark")

layout = [
    [sg.Text("voice.d file path (inf.d file must be in the same directory)", size=(60, 1))],
    [
        sg.InputText(key="-VB-"),
        sg.FileBrowse(file_types=(("voice.d file", "voice.d"),)),
    ],
    [sg.Text("output directory")],
    [
        sg.InputText(key="-OUT-"),
        sg.FolderBrowse(),
    ],
    [sg.Checkbox(key="-MERGE-", text="merge", enable_events=True)],
    [sg.Text(key="-OUTPUT-")],
    [sg.Button("Unpack"), sg.Button("More utils")],
]

window = sg.Window(
    "NIAONiao Unpacker (made by m and HHS_kt)",
    layout,
    resizable=False,
    icon=resource_path("./app.ico"),
)

while True:
    event, values = window.read(timeout=500)

    if finished:
        finished = False
        window["-OUTPUT-"].update(output_message, text_color="green")
        window["Unpack"].update(disabled=False)

    if error:
        error = False
        window["-OUTPUT-"].update("error: " + output_message, text_color="red")
        window["Unpack"].update(disabled=False)
        output_message = "Unknown"

    if event == sg.WIN_CLOSED:
        break
    elif event == "More utils":
        webbrowser.open("https://t.me/+AmQjUalgGFc3NTUy")
    elif event == "Unpack":
        vb_path = values["-VB-"]
        output_path = values["-OUT-"]
        should_merge = values["-MERGE-"]
        window["Unpack"].update(disabled=True)
        window["-OUTPUT-"].update("please wait...", text_color="yellow")
        threading.Thread(target=unpack_gui, daemon=True).start()
