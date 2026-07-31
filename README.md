# 🎮 Sudoku Game Modernization with GitHub Copilot

## Overview

This project focuses on improving a legacy Sudoku web application developed using Python and Flask. With the assistance of GitHub Copilot, the application was reorganized into a cleaner and more maintainable structure while introducing several gameplay enhancements, UI improvements, accessibility features, and automated testing.

Rather than simply accepting AI-generated code, GitHub Copilot was used as a development assistant to help analyze existing code, suggest implementations, generate tests, and improve the application's overall quality.

---

# Key Features

## Gameplay

* Generates Sudoku puzzles that always have a single valid solution.
* Supports three difficulty levels:

  * Easy
  * Medium
  * Hard
* Prevents editing of pre-filled cells.
* Validates user inputs in real time.
* Includes a **Check Puzzle** option to verify the current board.
* Provides a **Hint** feature that fills one correct value and locks that cell.
* Detects when the puzzle has been completed successfully.
* Displays a congratulatory message after completion.
* Tracks the total game time with a built-in timer.

---

## User Interface

* Responsive design for desktop, tablet, and mobile screens.
* Light and Dark mode support.
* Different background colors for each 3×3 Sudoku block to improve readability.
* Cleaner interface for better user experience.
* Accessibility improvements based on WCAG 2.1 AA recommendations.

---

## Leaderboard

A browser-based leaderboard records the fastest completed games.

Information stored includes:

* Player Name
* Completion Time
* Selected Difficulty
* Number of Hints Used

Additional functionality:

* Displays the Top 10 best scores.
* Uses browser Local Storage.
* Leaderboard data remains available after refreshing the page.

---

# Technologies Used

* Python 3
* Flask
* HTML5
* CSS3
* JavaScript
* GitHub Copilot
* Pytest

---

# Installation

### Clone the repository

```bash
git clone https://github.com/sejujam27/github-copilot-python.git
```

### Navigate to the project

```bash
cd github-copilot-python/starter
```

### Create a virtual environment

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install project dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Application

Start the Flask development server using:

```bash
flask --app app run
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

# Running Tests

Run the automated test suite using:

```bash
pytest
```

This command executes all tests inside the **tests** directory to verify that the application's main features work correctly.

---

# Project Structure

```text
github-copilot-python/
│
├── Screenshots/
├── starter/
│   ├── app.py
│   ├── instruction.md
│   ├── prompts.json
│   ├── requirements.txt
│   ├── static/
│   ├── sudoku/
│   ├── templates/
│   └── tests/
└── README.md
```

---

# Using GitHub Copilot

GitHub Copilot supported different stages of the project, including planning, development, testing, and UI improvements.

It was used to assist with:

* Refactoring the legacy application into modular code
* Improving code readability
* Implementing Sudoku puzzle generation
* Adding difficulty selection
* Creating the timer functionality
* Developing the Hint feature
* Implementing the Check Puzzle feature
* Adding real-time input validation
* Detecting puzzle completion
* Building the browser-based leaderboard
* Improving responsiveness
* Adding Dark Mode
* Enhancing accessibility
* Writing and validating automated tests

All generated suggestions were reviewed before being incorporated into the project.

---

# Evaluating GitHub Copilot Suggestions

During development, GitHub Copilot suggested multiple ways to implement the leaderboard.

One recommendation involved storing leaderboard data through a backend API, while another suggested using the browser's Local Storage.

After comparing both options, the Local Storage approach was selected because it fully met the project requirements while keeping the application lightweight and easy to maintain. A server-based solution was considered unnecessary for a locally stored Top 10 leaderboard.

This demonstrates thoughtful evaluation of Copilot's recommendations instead of accepting every suggestion without review.

---

# Screenshots

The **Screenshots** folder contains examples of GitHub Copilot prompts and responses related to:

* Refactoring the project structure
* Sudoku puzzle generation
* Setting up automated testing
* Implementing the Hint feature
* Creating the Top 10 leaderboard
* Styling the Sudoku grid
* Responsive UI improvements
* Accessibility enhancements
* Reviewing alternative Copilot-generated solutions

The **Final_Output** folder contains screenshots of the completed application.

---

# Additional Enhancements

The project also includes:

* Responsive design across multiple devices
* WCAG 2.1 AA accessibility improvements
* Dark and Light themes
* Reusable GitHub Copilot prompts stored in **prompts.json**

---

# Author

**Sejal Jambhulkar**

Bachelor of Engineering (Information Technology)

GitHub: https://github.com/sejujam27
