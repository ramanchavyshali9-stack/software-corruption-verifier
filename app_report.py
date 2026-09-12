import tkinter as tk
from tkinter import filedialog, messagebox
import zlib
import hashlib
import os
from datetime import datetime

# ============================================================
# SOFTWARE DOWNLOAD CORRUPTION VERIFIER
# ============================================================
# Features:
# 1. Select a software/file using Browse
# 2. Calculate file size
# 3. Calculate CRC-32
# 4. Compare with sample_software.txt (reference file)
# 5. Display SAFE / CORRUPTED
# 6. Maintain verification history
# 7. Clear current verification
# 8. Clear verification history
# ============================================================


REFERENCE_FILE = "sample_software.txt"
verification_history = []

# Dashboard statistics
total_checked = 0
safe_count = 0
corrupted_count = 0

def calculate_hashes(file_path):
    """Read a file and return (size, CRC-32, SHA-256)."""
    with open(file_path, "rb") as file:
        data = file.read()

    file_size = len(data)
    file_crc = zlib.crc32(data) & 0xFFFFFFFF
    file_sha256 = hashlib.sha256(data).hexdigest()

    return file_size, file_crc, file_sha256



def browse_file():
    """Select and verify a file."""
    global total_checked, safe_count, corrupted_count
    file_path = filedialog.askopenfilename(
        title="Select Software File",
        filetypes=[
            ("All Files", "*.*"),
            ("Text Files", "*.txt"),
            ("Executable Files", "*.exe"),
            ("ZIP Files", "*.zip"),
            ("PDF Files", "*.pdf")
        ]
    )

    if not file_path:
        return

    try:
        file_size, file_crc, file_sha256 = calculate_hashes(file_path)
        file_label.config(text="Selected: " + os.path.basename(file_path))
        path_label.config(text="Path: " + file_path)
        size_label.config(text="File Size: " + str(file_size) + " bytes")
        crc_label.config(text="CRC-32: " + format(file_crc, "08X"))
        sha256_label.config(text="SHA-256: " + file_sha256)

        # Check whether the reference file exists.
        if not os.path.exists(REFERENCE_FILE):
            result = "REFERENCE FILE NOT FOUND"
            result_label.config(text="RESULT: " + result)
            result_label.config(fg="orange")

            total_checked += 1
            update_statistics()

            add_to_history(
                os.path.basename(file_path),
                file_size,
                format(file_crc, "08X"),
                file_sha256,
                result
            )

            messagebox.showwarning(
                "Reference File Missing",
                "sample_software.txt was not found.\n\n"
                "Place sample_software.txt in the same folder as app.py "
                "to perform SAFE/CORRUPTED comparison."
            )
            return

        # Calculate CRC of the reference file.
        reference_size, reference_crc, reference_sha256 = calculate_hashes(REFERENCE_FILE)

        # Compare CRC values.
        if file_crc == reference_crc and file_sha256 == reference_sha256:
            result = "SAFE"
            result_label.config(
                text="RESULT: SAFE - File is not corrupted",
                fg="green"
            )
        else:
            result = "CORRUPTED"
            result_label.config(
                text="RESULT: CORRUPTED - File has changed",
                fg="red"
            )

        total_checked += 1
        if result == "SAFE":
            safe_count += 1
        elif result == "CORRUPTED":
            corrupted_count += 1

        update_statistics()

        add_to_history(
            os.path.basename(file_path),
            file_size,
            format(file_crc, "08X"),
            file_sha256,
            result
        )

    except Exception as error:
        messagebox.showerror(
            "Verification Error",
            "Unable to verify the selected file.\n\n" + str(error)
        )


def add_to_history(file_name, file_size, crc, sha256, result):
    """Add one verification result to the history list and display."""
    verification_history.append({
        "file": file_name,
        "size": file_size,
        "crc": crc,
        "sha256": sha256,
        "result": result,
        "time": datetime.now().strftime("%H:%M:%S")
    })

    update_history_display()
def update_history_display():
    """Refresh the verification history display."""
    history_text.config(state="normal")
    history_text.delete("1.0", tk.END)

    if not verification_history:
        history_text.insert(
            tk.END,
            "No verification history yet."
        )
    else:
        history_text.insert(
            tk.END,
            "TIME       FILE                         SIZE       CRC-32      SHA-256                           RESULT\n"
        )
        history_text.insert(
            tk.END,
            "-" * 82 + "\n"
        )

        for item in verification_history:
            line = (
                f"{item['time']:<10} "
                f"{item['file'][:27]:<27} "
                f"{item['size']:<10} "
                f"{item['crc']:<10} "
                f"{item['sha256'][:20]:<20} "
                f"{item['result']}\n"
            )
            history_text.insert(tk.END, line)

    history_text.config(state="disabled")


def update_statistics():
    """Refresh dashboard statistics."""
    total_label.config(text="TOTAL CHECKED\n" + str(total_checked))
    safe_stat_label.config(text="SAFE FILES\n" + str(safe_count))
    corrupted_stat_label.config(text="CORRUPTED FILES\n" + str(corrupted_count))


def clear_data():
    """Clear the current verification result."""
    file_label.config(text="No file selected")
    path_label.config(text="Path: -")
    size_label.config(text="File Size: -")
    crc_label.config(text="CRC-32: -")
    sha256_label.config(text="SHA-256: -")

    result_label.config(
        text="RESULT: Waiting for verification",
        fg="black"
    )


def generate_report():
    """Save the current verification history as a text report."""
    if not verification_history:
        messagebox.showinfo(
            "No History",
            "Please verify at least one file before generating a report."
        )
        return

    report_path = filedialog.asksaveasfilename(
        title="Save Verification Report",
        defaultextension=".txt",
        filetypes=[
            ("Text Report", "*.txt"),
            ("All Files", "*.*")
        ],
        initialfile="verification_report.txt"
    )

    if not report_path:
        return

    try:
        with open(report_path, "w", encoding="utf-8") as report:
            report.write("SOFTWARE DOWNLOAD CORRUPTION VERIFICATION REPORT\n")
            report.write("=" * 70 + "\n\n")

            report.write("DASHBOARD SUMMARY\n")
            report.write("-" * 70 + "\n")
            report.write(f"Total Files Checked : {total_checked}\n")
            report.write(f"Safe Files          : {safe_count}\n")
            report.write(f"Corrupted Files     : {corrupted_count}\n\n")

            report.write("VERIFICATION DETAILS\n")
            report.write("-" * 70 + "\n")

            for number, item in enumerate(verification_history, start=1):
                report.write(f"Verification #{number}\n")
                report.write(f"Time       : {item['time']}\n")
                report.write(f"File Name  : {item['file']}\n")
                report.write(f"File Size  : {item['size']} bytes\n")
                report.write(f"CRC-32     : {item['crc']}\n")
                report.write(f"SHA-256    : {item['sha256']}\n")
                report.write(f"Result     : {item['result']}\n")
                report.write("-" * 70 + "\n")

            report.write("\nEND OF REPORT\n")

        messagebox.showinfo(
            "Report Generated",
            "Verification report saved successfully.\n\n"
            + report_path
        )

    except Exception as error:
        messagebox.showerror(
            "Report Error",
            "Unable to save the report.\n\n" + str(error)
        )


def clear_history():
    """Clear all verification history and dashboard statistics."""
    global total_checked, safe_count, corrupted_count

    verification_history.clear()
    total_checked = 0
    safe_count = 0
    corrupted_count = 0

    update_history_display()
    update_statistics()


# ============================================================
# MAIN WINDOW
# ============================================================

window = tk.Tk()
window.title("Software Download Corruption Verifier")
window.geometry("1000x1200")
window.resizable(False, False)

# Main title
title = tk.Label(
    window,
    text="SOFTWARE DOWNLOAD CORRUPTION VERIFIER",
    font=("Arial", 20, "bold")
)
title.pack(pady=(20, 10))

# Description
message = tk.Label(
    window,
    text="Select a software file to verify its integrity using CRC-32.",
    font=("Arial", 12)
)
message.pack(pady=5)

# ============================================================
# DASHBOARD STATISTICS
# ============================================================

stats_frame = tk.Frame(window)
stats_frame.pack(pady=8)

total_label = tk.Label(
    stats_frame,
    text="TOTAL CHECKED\n0",
    font=("Arial", 12, "bold"),
    width=20,
    height=2,
    relief="groove",
    bd=2
)
total_label.pack(side="left", padx=8)

safe_stat_label = tk.Label(
    stats_frame,
    text="SAFE FILES\n0",
    font=("Arial", 12, "bold"),
    width=20,
    height=2,
    relief="groove",
    bd=2
)
safe_stat_label.pack(side="left", padx=8)

corrupted_stat_label = tk.Label(
    stats_frame,
    text="CORRUPTED FILES\n0",
    font=("Arial", 12, "bold"),
    width=20,
    height=2,
    relief="groove",
    bd=2
)
corrupted_stat_label.pack(side="left", padx=8)

# Browse button
browse_button = tk.Button(
    window,
    text="BROWSE FILE",
    font=("Arial", 14, "bold"),
    width=18,
    command=browse_file
)
browse_button.pack(pady=15)

# Current verification frame
current_frame = tk.LabelFrame(
    window,
    text="Current Verification",
    font=("Arial", 12, "bold"),
    padx=15,
    pady=10
)
current_frame.pack(fill="x", padx=30, pady=5)

file_label = tk.Label(
    current_frame,
    text="No file selected",
    font=("Arial", 12)
)
file_label.pack(pady=5)

path_label = tk.Label(
    current_frame,
    text="Path: -",
    font=("Arial", 10),
    wraplength=850
)
path_label.pack(pady=3)

size_label = tk.Label(
    current_frame,
    text="File Size: -",
    font=("Arial", 12)
)
size_label.pack(pady=5)

crc_label = tk.Label(
    current_frame,
    text="CRC-32: -",
    font=("Arial", 12, "bold")
)
crc_label.pack(pady=5)

sha256_label = tk.Label(
    current_frame,
    text="SHA-256: -",
    font=("Arial", 10, "bold"),
    wraplength=850
)
sha256_label.pack(pady=5)

result_label = tk.Label(
    current_frame,
    text="RESULT: Waiting for verification",
    font=("Arial", 14, "bold")
)
result_label.pack(pady=8)

# Current clear button
clear_button = tk.Button(
    current_frame,
    text="CLEAR",
    font=("Arial", 12, "bold"),
    width=12,
    command=clear_data
)
clear_button.pack(pady=5)
# Generate report button
report_button = tk.Button(
    window,
    text="GENERATE REPORT",
    font=("Arial", 11, "bold"),
    width=18,
    command=generate_report
)
report_button.pack(pady=(0, 8))

# Verification history frame
history_frame = tk.LabelFrame(
    window,
    text="Verification History",
    font=("Arial", 12, "bold"),
    padx=10,
    pady=10
)
history_frame.pack(fill="both", expand=True, padx=30, pady=15)

history_text = tk.Text(
    history_frame,
    height=10,
    width=105,
    font=("Courier New", 10),
    wrap="none"
)
history_text.pack(side="left", fill="both", expand=True)

history_scrollbar = tk.Scrollbar(
    history_frame,
    command=history_text.yview
)
history_scrollbar.pack(side="right", fill="y")

history_text.config(yscrollcommand=history_scrollbar.set)
history_text.config(state="disabled")



# Clear history button
clear_history_button = tk.Button(
    window,
    text="CLEAR HISTORY",
    font=("Arial", 11, "bold"),
    width=18,
    command=clear_history
)
clear_history_button.pack(pady=(0, 15))

# Initial history and statistics display
update_history_display()
update_statistics()

# Start dashboard
window.mainloop()
