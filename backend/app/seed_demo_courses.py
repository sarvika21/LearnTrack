"""
Insert two complete LearnTrack demo courses into MongoDB Atlas.

Run from the backend directory:
    python -m app.seed_demo_courses

Safe to run more than once: existing demo courses are updated, not duplicated.
"""
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import ObjectId

from app.database.connection import connect_database

NOW = datetime.now(timezone.utc)

COURSES = [
    {
        "seed_key": "demo-python-fundamentals",
        "title": "Python Programming Fundamentals",
        "description": "Learn Python from the ground up: variables, data types, conditions, loops, functions, and problem solving. Includes short lessons and knowledge-check quizzes.",
        "category": "Programming",
        "level": "Beginner",
        "published": True,
        "lessons": [
            {
                "order": 1,
                "title": "Introduction to Python",
                "content": """Learning objectives
• Understand what Python is and where it is used.
• Recognise the basic structure of a Python program.
• Use print() to display information.

What is Python?
Python is a high-level, general-purpose programming language known for readable syntax. It is used in web development, automation, data analysis, artificial intelligence, and scripting.

Your first program
    print("Hello, LearnTrack!")

The print() function displays text or values in the console. Text is written inside quotation marks.

Comments
A comment begins with #. Python ignores comments when running a program.
    # This is my first Python comment
    print("Welcome")

Remember: Python uses indentation to group statements. Consistent indentation is important.""",
                "video_url": None,
                "quiz": {
                    "title": "Python Basics Quiz",
                    "pass_mark": 60,
                    "questions": [
                        {
                            "question": "Which function displays output in Python?",
                            "options": ["input()", "print()", "displayText()", "show()"],
                            "answer_index": 1,
                            "explanation": "print() displays output in the console."
                        },
                        {
                            "question": "Which symbol starts a single-line comment in Python?",
                            "options": ["//", "/*", "#", "<!--"],
                            "answer_index": 2,
                            "explanation": "The hash symbol (#) starts a Python comment."
                        },
                        {
                            "question": "Which is a valid Python string?",
                            "options": ["Hello", "'Hello'", "{Hello}", "<Hello>"],
                            "answer_index": 1,
                            "explanation": "String text must be enclosed in quotes."
                        }
                    ]
                }
            },
            {
                "order": 2,
                "title": "Variables and Data Types",
                "content": """Learning objectives
• Create and assign variables.
• Identify common Python data types.
• Convert values between types.

Variables
A variable is a name that refers to a value. Python creates a variable when you assign a value:
    student_name = "Anu"
    age = 19
    cgpa = 8.4

Common data types
• str — text, for example "LearnTrack"
• int — whole numbers, for example 25
• float — decimal numbers, for example 8.5
• bool — True or False

Check a value's type with type():
    print(type(age))

Type conversion
    number_text = "42"
    number = int(number_text)

Variable names are case-sensitive. Use meaningful names and do not start a variable name with a number.""",
                "video_url": None,
                "quiz": {
                    "title": "Variables and Data Types Quiz",
                    "pass_mark": 60,
                    "questions": [
                        {
                            "question": "Which data type stores a decimal number?",
                            "options": ["int", "float", "str", "bool"],
                            "answer_index": 1,
                            "explanation": "float represents numbers with a fractional part."
                        },
                        {
                            "question": "What is the value of type('LearnTrack')?",
                            "options": ["int", "float", "str", "bool"],
                            "answer_index": 2,
                            "explanation": "Text enclosed in quotes is a string (str)."
                        },
                        {
                            "question": "Which assignment creates a variable named score?",
                            "options": ["score == 10", "10 = score", "score = 10", "var score := 10"],
                            "answer_index": 2,
                            "explanation": "The assignment operator = assigns the value 10 to score."
                        }
                    ]
                }
            },
            {
                "order": 3,
                "title": "Conditions and Loops",
                "content": """Learning objectives
• Make decisions with if, elif, and else.
• Repeat instructions with for and while loops.

Conditional statements
    mark = 75
    if mark >= 50:
        print("Pass")
    else:
        print("Try again")

The condition is evaluated as True or False. The matching block runs.

For loop
    for number in range(1, 4):
        print(number)

This prints 1, 2, and 3. The ending value in range() is not included.

While loop
    count = 1
    while count <= 3:
        print(count)
        count += 1

Make sure a while loop eventually reaches a condition that is False, otherwise it may run forever.""",
                "video_url": None,
                "quiz": {
                    "title": "Conditions and Loops Quiz",
                    "pass_mark": 60,
                    "questions": [
                        {
                            "question": "Which keyword is used when the if condition is false and an alternative branch is needed?",
                            "options": ["repeat", "else", "then", "case"],
                            "answer_index": 1,
                            "explanation": "else provides the alternative branch."
                        },
                        {
                            "question": "How many values does range(1, 4) produce?",
                            "options": ["2", "3", "4", "5"],
                            "answer_index": 1,
                            "explanation": "It produces 1, 2, and 3."
                        },
                        {
                            "question": "Which loop is commonly used to iterate over a sequence?",
                            "options": ["for", "switch", "select", "repeat-until"],
                            "answer_index": 0,
                            "explanation": "A for loop iterates over items in a sequence."
                        }
                    ]
                }
            }
        ]
    },
    {
        "seed_key": "demo-web-development",
        "title": "Web Development Essentials",
        "description": "Build a strong foundation in the web: understand HTML page structure, style pages with CSS, and add simple interactions with JavaScript.",
        "category": "Web Development",
        "level": "Beginner",
        "published": True,
        "lessons": [
            {
                "order": 1,
                "title": "HTML: Structure of a Web Page",
                "content": """Learning objectives
• Explain the purpose of HTML.
• Identify common HTML elements.
• Create a basic HTML document.

HTML means HyperText Markup Language. It describes the structure and content of a web page using elements (tags).

Basic document
    <!doctype html>
    <html>
      <head>
        <title>My First Page</title>
      </head>
      <body>
        <h1>Hello, world!</h1>
        <p>Welcome to my website.</p>
      </body>
    </html>

Common elements
• h1 to h6: headings
• p: paragraph
• a: hyperlink
• img: image
• ul, ol, li: lists
• div: generic block container

Most elements have an opening tag and a closing tag. Some elements, such as img, are void elements and do not need a closing tag.""",
                "video_url": None,
                "quiz": {
                    "title": "HTML Structure Quiz",
                    "pass_mark": 60,
                    "questions": [
                        {
                            "question": "What does HTML stand for?",
                            "options": ["HyperText Markup Language", "HighText Machine Language", "Hyper Tool Multi Language", "Home Text Markup Link"],
                            "answer_index": 0,
                            "explanation": "HTML stands for HyperText Markup Language."
                        },
                        {
                            "question": "Which element creates the largest standard heading?",
                            "options": ["<head>", "<h1>", "<p>", "<title>"],
                            "answer_index": 1,
                            "explanation": "h1 is the highest-level heading element."
                        },
                        {
                            "question": "Which element creates a hyperlink?",
                            "options": ["<linkto>", "<a>", "<href>", "<url>"],
                            "answer_index": 1,
                            "explanation": "The a element creates a hyperlink using its href attribute."
                        }
                    ]
                }
            },
            {
                "order": 2,
                "title": "CSS: Styling a Web Page",
                "content": """Learning objectives
• Describe the role of CSS.
• Use selectors and declarations.
• Apply colours, spacing, and layout.

CSS means Cascading Style Sheets. It controls how HTML content looks.

Example
    h1 {
      color: navy;
      font-size: 32px;
    }

A CSS rule contains a selector and a declaration block. Each declaration has a property and a value.

Ways to add CSS
• Inline CSS: a style attribute on an element.
• Internal CSS: a style element in the HTML head.
• External CSS: a separate .css file linked with a link element.

External stylesheets are useful because one file can style many pages. Common properties include color, background-color, margin, padding, border, and display.""",
                "video_url": None,
                "quiz": {
                    "title": "CSS Styling Quiz",
                    "pass_mark": 60,
                    "questions": [
                        {
                            "question": "What does CSS control?",
                            "options": ["Database storage", "The visual presentation of web pages", "Server authentication", "Network routing"],
                            "answer_index": 1,
                            "explanation": "CSS controls the presentation and layout of HTML content."
                        },
                        {
                            "question": "Which symbol begins a class selector in CSS?",
                            "options": ["#", ".", "@", "&"],
                            "answer_index": 1,
                            "explanation": "A dot (.) selects elements by class."
                        },
                        {
                            "question": "Which property changes the text colour?",
                            "options": ["font-style", "background", "color", "text-size"],
                            "answer_index": 2,
                            "explanation": "The color property sets text colour."
                        }
                    ]
                }
            },
            {
                "order": 3,
                "title": "JavaScript: Adding Interactivity",
                "content": """Learning objectives
• Explain why JavaScript is used.
• Declare variables.
• Respond to a button click.

JavaScript is a programming language commonly used in browsers to make web pages interactive.

Variables
    const courseName = "LearnTrack";
    let score = 0;

Use const when a binding should not be reassigned and let when it may change.

Functions
    function greet(name) {
      return "Hello, " + name;
    }

DOM interaction
    document.querySelector("h1").textContent = "Welcome!";

Events
    document.querySelector("button").addEventListener("click", function () {
      alert("Button clicked!");
    });

JavaScript can respond to user actions, update page content, validate forms, and communicate with backend APIs.""",
                "video_url": None,
                "quiz": {
                    "title": "JavaScript Basics Quiz",
                    "pass_mark": 60,
                    "questions": [
                        {
                            "question": "Which keyword declares a block-scoped variable that can be reassigned?",
                            "options": ["let", "fixed", "define", "static"],
                            "answer_index": 0,
                            "explanation": "let declares a block-scoped variable that can be reassigned."
                        },
                        {
                            "question": "Which method attaches an event handler?",
                            "options": ["queryEvent()", "addEventListener()", "attachHTML()", "listenClick()"],
                            "answer_index": 1,
                            "explanation": "addEventListener() registers an event listener."
                        },
                        {
                            "question": "Which browser object provides access to the page structure?",
                            "options": ["MongoDB", "DOM", " pip", "FastAPI"],
                            "answer_index": 1,
                            "explanation": "The DOM represents the document as a tree of objects."
                        }
                    ]
                }
            }
        ]
    }
]


def main():
    db = connect_database()
    courses_col = db["courses"]
    lessons_col = db["lessons"]
    quizzes_col = db["quizzes"]

    created_courses = 0
    updated_courses = 0
    created_lessons = 0
    updated_lessons = 0
    created_quizzes = 0
    updated_quizzes = 0

    for course_data in COURSES:
        course_doc = {k: v for k, v in course_data.items() if k != "lessons"}
        course_doc["updated_at"] = NOW
        existing_course = courses_col.find_one({"seed_key": course_data["seed_key"]})

        if existing_course:
            course_id = existing_course["_id"]
            courses_col.update_one({"_id": course_id}, {"$set": course_doc})
            updated_courses += 1
        else:
            course_doc["created_at"] = NOW
            course_id = courses_col.insert_one(course_doc).inserted_id
            created_courses += 1

        for lesson_data in course_data["lessons"]:
            lesson_doc = {
                "title": lesson_data["title"],
                "content": lesson_data["content"],
                "video_url": lesson_data["video_url"],
                "order": lesson_data["order"],
                "course_id": str(course_id),
                "created_at": NOW,
            }
            existing_lesson = lessons_col.find_one({
                "course_id": str(course_id),
                "order": lesson_data["order"],
            })

            if existing_lesson:
                lesson_id = existing_lesson["_id"]
                lessons_col.update_one({"_id": lesson_id}, {"$set": lesson_doc})
                updated_lessons += 1
            else:
                lesson_id = lessons_col.insert_one(lesson_doc).inserted_id
                created_lessons += 1

            quiz_data = lesson_data["quiz"]
            quiz_doc = {
                "lesson_id": str(lesson_id),
                "course_id": str(course_id),
                "title": quiz_data["title"],
                "questions": quiz_data["questions"],
                "pass_mark": quiz_data["pass_mark"],
                "updated_at": NOW,
            }
            result = quizzes_col.update_one(
                {"lesson_id": str(lesson_id)},
                {"$set": quiz_doc, "$setOnInsert": {"created_at": NOW}},
                upsert=True,
            )
            if result.upserted_id:
                created_quizzes += 1
            else:
                updated_quizzes += 1

    print("\nLearnTrack demo content is ready!")
    print(f"Courses: 2 ({created_courses} created, {updated_courses} updated)")
    print(f"Lessons: 6 ({created_lessons} created, {updated_lessons} updated)")
    print(f"Quizzes: 6 ({created_quizzes} created, {updated_quizzes} updated)")
    print("\nOpen the app, sign in as Admin, and click Courses.")
    print("For the student view, sign out and register/sign in as a Student.")


if __name__ == "__main__":
    main()
