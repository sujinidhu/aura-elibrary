import os
from datetime import datetime
from urllib.parse import quote
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'aura_premium_key')

# --- DATABASE CONFIGURATION (Supabase in cloud, SQLite locally) ---
db_url = os.environ.get("DATABASE_URL", "sqlite:///aura_local.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    quiz = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

# --- 1. LOGIN CREDENTIALS ---
VALID_USERNAME = "admin"
VALID_PASSWORD = "1234"

# --- SUPABASE STORAGE AUTO-LINK HELPER ---
SUPABASE_PROJECT_ID = "zyhlzatoiyrasffyqlki"
BUCKET_NAME = "notes"  # Change to "notes" if you named your Supabase bucket "notes"

def pdf_url(filename):
    base = f"https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public/{BUCKET_NAME}/"
    return base + quote(filename)

# --- 2. DATASETS ---
LIBRARY_BOOKS = [
    {"id": 1, "title": "Programming in ANSI C", "category": "AUTHOR:BALAGURU SWAMY", "image": "static/WhatsApp Image 2026-04-25 at 3.07.20 PM.jpeg", "link": pdf_url("Programming in ANSI C (E Balagurusamy) (Z-Library).pdf")},
    {"id": 2, "title": "Fundamentals of Computers", "category": "BCA Core", "image": "static/61vhaWXjshL._SY425_ (1).jpg", "link": pdf_url("Anita-Goel-Computer-Fundamentals-Pearson-2010.pdf")},
    {"id": 3, "title": "Mathematical Foundation", "category": "BCA Core", "image": "static/images (1).jpg", "link": pdf_url("kunen7701.pdf")},
    {"id": 4, "title": "Data Structure using C", "category": "BCA Core", "image": "static/515p4XIZoQL._AC_UF1000,1000_QL80_ (1).jpg", "link": pdf_url("data-structures-and-algorithms-with-c-9781783323685_compress.pdf")},
    {"id": 5, "title": "Object Oriented Programming with JAVA", "category": "BCA core", "image": "static/Screenshot_2026-04-24-20-35-19-53_e5d3893ac03954c6bb675ef2555b879b.jpg", "link": pdf_url("Herbert Schildt - Java_ The Complete Reference-McGraw-Hill Osborne Media (2006).pdf")},
    {"id": 6, "title": "Discrete Mathematical Structures", "category": "BCA Core", "image": "static/Screenshot_2026-04-24-20-34-48-68_e5d3893ac03954c6bb675ef2555b879b.jpg", "link": pdf_url("Discrete Mathematics.pdf")},
    {"id": 7, "title": "C# and .NET Framework", "category": "BCA Core", "image": "static/Screenshot 2026-04-24 205438.png", "link": pdf_url("6_2017_05_21!12_07_57_AM.pdf")},
    {"id": 8, "title": "Database Management Systems", "category": "BCA Core", "image": "static/Screenshot 2026-04-24 204412.png", "link": pdf_url("Database Management System.pdf")},
    {"id": 9, "title": "Computer Communication and Networks", "category": "BCA Core", "image": "static/Screenshot_2026-04-24-20-30-48-97_e5d3893ac03954c6bb675ef2555b879b.jpg", "link": pdf_url("9780133814743.pdf")},
    {"id": 10, "title": "Computer Multimedia and Animation", "category": "BCA Core", "image": "static/Screenshot_2026-04-24-20-37-30-07_e5d3893ac03954c6bb675ef2555b879b.jpg", "link": pdf_url("Computer Multimedia Animation.pdf")},
    {"id": 11, "title": "Python Programming", "category": "BCA Core", "image": "static/Screenshot 2026-04-24 204528.png", "link": pdf_url("Introduction_to_Python_Programming_-_WEB.pdf")},
    {"id": 12, "title": "Operating System Concepts", "category": "BCA Core", "image": "static/Screenshot 2026-04-24 204607.png", "link": pdf_url("Abraham Silberschatz-Operating System Concepts (9th,2012_12).pdf")},
    {"id": 13, "title": "Statistical Computing and R Programming", "category": "BCA Core", "image": "static/Screenshot_2026-04-24-20-30-08-54_e5d3893ac03954c6bb675ef2555b879b.jpg", "link": pdf_url("SCR.pdf")},
    {"id": 14, "title": "Design and Analysis of Algorithms", "category": "BCA Core", "image": "static/Screenshot_2026-04-24-20-35-56-45_e5d3893ac03954c6bb675ef2555b879b.jpg", "link": pdf_url("Design and Analysis of Algorithms.pdf")},
    {"id": 15, "title": "Software Engineering", "category": "BCA Core", "image": "static/Screenshot_2026-04-24-20-36-58-77_e5d3893ac03954c6bb675ef2555b879b.jpg", "link": pdf_url("Software Engineering.pdf")},
    {"id": 16, "title": "Hypertext preprocessor", "category": "php", "image": "static/Screenshot_2026-04-24-20-31-17-25_e5d3893ac03954c6bb675ef2555b879b.jpg", "link": pdf_url("9780321833891.pdf")},
    {"id": 17, "title": "Web Content Management System", "category": "WCMS", "image": "static/download (1).jpg", "link": pdf_url("WCMS.pdf")},
    {"id": 18, "title": "J2EE", "category": "BCA Core", "image": "static/download (1) (1).jpg", "link": pdf_url("j2ee-1_3-doc-tutorial-draft5.pdf")}
]

STUDY_MATERIALS = [
    {"title": "Programming in ANSI C", "type": "PDF", "link": pdf_url("BSCIT 102 C Lang.pdf")},
    {"title": "Fundamentals of Computers", "type": "PDF", "link": pdf_url("computer_fundamental.pdf")},
    {"title": "Mathematical Foundation", "type": "PDF", "link": pdf_url("Lecture-notes.pdf")},
    {"title": "Data Structure using C", "type": "PDF", "link": pdf_url("Data Structures using C.pdf")},
    {"title": "Object Oriented Programming with JAVA", "type": "PDF", "link": pdf_url("Java.pdf")},
    {"title": "Discrete Mathematical Structures", "type": "PDF", "link": pdf_url("DISCRETE MATHEMATICS NOTES.pdf")},
    {"title": "C# and .NET Framework", "type": "PDF", "link": pdf_url("dotNET.pdf")},
    {"title": "Database Management Systems", "type": "PDF", "link": pdf_url("DBMS.pdf")},
    {"title": "Computer Communication and Networks", "type": "PDF", "link": pdf_url("Computer Communication Networks.pdf")},
    {"title": "Computer Multimedia and Animation", "type": "PDF", "link": pdf_url("Computer Multimedia & Animation (1).pdf")},
    {"title": "Python Programming", "type": "PDF", "link": pdf_url("Python.pdf")},
    {"title": "Operating System Concepts", "type": "PDF", "link": pdf_url("Operating System Concepts.pdf")},
    {"title": "Statistical Computing and R Programming", "type": "PDF", "link": pdf_url("Statistical Computing and R Programming.pdf")},
    {"title": "Design and Analysis of Algorithms", "type": "PDF", "link": pdf_url("ADA study materials.pdf")},
    {"title": "Software Engineering", "type": "PDF", "link": pdf_url("software engineering study.pdf")},
    {"title": "Hypertext preprocessor", "type": "PDF", "link": pdf_url("PHP.pdf")},
    {"title": "Web Content Management System", "type": "PDF", "link": pdf_url("WCMS STUDY MATERLAS OF BCA AND BCOM-CA.pdf")},
    {"title": "J2EE", "type": "PDF", "link": pdf_url("VI SEM BCA-Advanced JAVA and J2EE(MVC)-STUDY MATERILAS (1).pdf")}
]

QUIZ_DATA = {
    "programming in ANSI C": {
        "title": "Programming in ANSI C",
        "questions": [
            {"q": "Where does execution of a C program start?", "options": ["main()", "start()", "init()", "program()"], "answer": "main()"},
            {"q": "Which symbol is used to end a C statement?", "options": [".", ",", ";", ":"], "answer": ";"},
            {"q": "Which of the following is a valid comment in C?", "options": ["// comment", "/* comment */", "# comment", "<!-- comment -->"], "answer": "/* comment */"},
            {"q": "Which of the following is a preprocessor directive?", "options": ["printf()", "#include", "main()", "return"], "answer": "#include"},
            {"q": "Which function is used to print output in C?", "options": ["scanf()", "print()", "printf()", "output()"], "answer": "printf()"},
            {"q": "Which data type is used to store a single character?", "options": ["int", "char", "float", "double"], "answer": "char"},
            {"q": "Which keyword is used to declare a constant variable?", "options": ["final", "const", "static", "define"], "answer": "const"},
            {"q": "What is the size of char data type (typically)?", "options": ["4 bits", "8 bits", "16 bits", "32 bits"], "answer": "8 bits"},
            {"q": "Which operator is used for assignment in C?", "options": ["==", "=", ":", "!="], "answer": "="},
            {"q": "Which operator is used to find remainder in C?", "options": ["/", "%", "*", "+"], "answer": "%"},
            {"q": "Which of the following is a valid variable name?", "options": ["1var", "_var", "var-name", "int"], "answer": "_var"},
            {"q": "Which of the following is NOT a valid data type in C?", "options": ["int", "float", "string", "char"], "answer": "string"},
            {"q": "Which symbol is used for address-of operator?", "options": ["*", "&", "%", "#"], "answer": "&"},
            {"q": "Which loop executes at least once?", "options": ["for", "while", "do-while", "if"], "answer": "do-while"},
            {"q": "Which keyword is used to return a value from a function?", "options": ["exit", "return", "break", "continue"], "answer": "return"},
            {"q": "Which operator is used to compare equality?", "options": ["=", "==", "!=", "<>"], "answer": "=="},
            {"q": "Which of the following is used to declare a pointer?", "options": ["&", "*", "%", "#"], "answer": "*"},
            {"q": "Which function is used to read input from user?", "options": ["printf()", "input()", "scanf()", "read()"], "answer": "scanf()"},
            {"q": "Which storage class is used for global variables?", "options": ["auto", "register", "extern", "local"], "answer": "extern"},
            {"q": "Which of the following is used to group statements in C?", "options": ["()", "[]", "{}", "<>"], "answer": "{}"}
        ]
    },
    "Fundamentals of Computers": {
        "title": "Fundamentals of Computers",
        "questions": [
            {"q": "Which of the following best defines a computer?", "options": ["An electronic device for processing data", "A mechanical calculator", "A storage-only device", "A communication-only device"], "answer": "An electronic device for processing data"},
            {"q": "Which of the following is volatile memory?", "options": ["ROM", "RAM", "Hard Disk", "DVD"], "answer": "RAM"},
            {"q": "Which of the following is non-volatile memory?", "options": ["RAM", "Cache", "ROM", "Registers"], "answer": "ROM"},
            {"q": "What is an algorithm?", "options": ["A step-by-step procedure to solve a problem", "A programming language", "A hardware device", "A type of memory"], "answer": "A step-by-step procedure to solve a problem"},
            {"q": "Which of the following is used to visually represent an algorithm?", "options": ["Flowchart", "Compiler", "Interpreter", "Assembler"], "answer": "Flowchart"},
            {"q": "Which tool translates high-level language into machine code?", "options": ["Compiler", "Interpreter", "Assembler", "Debugger"], "answer": "Compiler"},
            {"q": "Convert decimal 123 to binary.", "options": ["1111011", "1110111", "1101101", "1111101"], "answer": "1111011"},
            {"q": "Convert decimal 90 to binary.", "options": ["1011010", "1010110", "1001010", "1101010"], "answer": "1011010"},
            {"q": "Which principle states that every Boolean expression has a dual?", "options": ["Duality Principle", "Idempotent Law", "Associative Law", "Distributive Law"], "answer": "Duality Principle"},
            {"q": "Truth table of AND gate gives output 1 when:", "options": ["Any input is 1", "All inputs are 1", "All inputs are 0", "Inputs are different"], "answer": "All inputs are 1"},
            {"q": "Which of the following is a characteristic of first-generation computers?", "options": ["Used vacuum tubes", "Used microprocessors", "Used transistors", "Used integrated circuits"], "answer": "Used vacuum tubes"},
            {"q": "Which of the following is an example of a word processor?", "options": ["MS Word", "MS Excel", "MS PowerPoint", "Adobe Photoshop"], "answer": "MS Word"},
            {"q": "Which of the following is an image editor?", "options": ["MS Word", "MS Excel", "Adobe Photoshop", "MS Access"], "answer": "Adobe Photoshop"},
            {"q": "Which of the following is NOT a system utility?", "options": ["Disk Cleanup", "Antivirus", "Text Editor", "File Compression"], "answer": "Text Editor"},
            {"q": "Which of the following is an advantage of assembly language?", "options": ["Closer to hardware", "Easier than high-level languages", "Portable across systems", "Independent of hardware"], "answer": "Closer to hardware"},
            {"q": "Which of the following is a Boolean algebra theorem?", "options": ["x + x' = 1", "x + 0 = 0", "x · x = 0", "x + 1 = 0"], "answer": "x + x' = 1"},
            {"q": "Which gate outputs the inverse of AND?", "options": ["NAND", "NOR", "XOR", "XNOR"], "answer": "NAND"},
            {"q": "Which gate outputs 1 only when inputs are different?", "options": ["XOR", "XNOR", "AND", "OR"], "answer": "XOR"},
            {"q": "Which number system uses base 16?", "options": ["Binary", "Octal", "Decimal", "Hexadecimal"], "answer": "Hexadecimal"},
            {"q": "Which protocol is used for browsing the World Wide Web?", "options": ["HTTP", "FTP", "SMTP", "POP3"], "answer": "HTTP"}
        ]
    },
    "Mathematical Foundation": {
        "title": "Mathematical Foundation",
        "questions": [
            {"q": "What is the binomial theorem?", "options": ["(a+b)^n expansion", "Sum of logs", "Matrix property", "Differentiation rule"], "answer": "(a+b)^n expansion"},
            {"q": "Find log4(256).", "options": ["2", "4", "6", "8"], "answer": "4"},
            {"q": "Find log2(64).", "options": ["4", "5", "6", "7"], "answer": "6"},
            {"q": "Centroid of triangle with vertices (3,-2), (-1,-4), (-5,6)?", "options": ["(-1,0)", "(-1, -2)", "(-1, 0)", "(-1, 2)"], "answer": "(-1,0)"},
            {"q": "Convert 90° to radians.", "options": ["π/2", "π/3", "π/4", "π"], "answer": "π/2"},
            {"q": "Convert 135° to radians.", "options": ["3π/4", "π/2", "π/3", "π"], "answer": "3π/4"},
            {"q": "Differentiate 4x^3 - 7x^4.", "options": ["12x^2 - 28x^3", "12x^2 - 21x^3", "3x^2 - 7x^3", "None"], "answer": "12x^2 - 28x^3"},
            {"q": "Define diagonal matrix.", "options": ["All elements zero", "Non-diagonal elements zero", "All ones", "Symmetric matrix"], "answer": "Non-diagonal elements zero"},
            {"q": "Find first term and common difference if nth term = 7n - 3.", "options": ["a=4, d=7", "a=7, d=3", "a=3, d=7", "a=4, d=3"], "answer": "a=4, d=7"},
            {"q": "Define echelon form of a matrix.", "options": ["Diagonal form", "Row-reduced form", "Symmetric form", "Identity form"], "answer": "Row-reduced form"},
            {"q": "Equation of line through (2,4) perpendicular to 5x-7y=100?", "options": ["7x+5y=c", "7x-5y=c", "5x+7y=c", "None"], "answer": "7x+5y=c"},
            {"q": "Quadrilateral with points (2,-1),(3,4),(-2,3),(-3,-2) is?", "options": ["Square", "Rectangle", "Rhombus", "Parallelogram"], "answer": "Rhombus"},
            {"q": "Centre of circle x^2+y^2-4x+8y-5=0?", "options": ["(2,-4)", "(2,-8)", "(2,-4)", "(2,4)"], "answer": "(2,-4)"},
            {"q": "Radius of circle x^2+y^2-4x+8y-5=0?", "options": ["5", "√25", "√20", "√21"], "answer": "√21"},
            {"q": "Value of tan45° + cot45°?", "options": ["2", "1", "0", "∞"], "answer": "2"},
            {"q": "lim (2x^2-7x+6)/(5x^2-11x+2) as x→2?", "options": ["0", "1", "2", "∞"], "answer": "0"},
            {"q": "Differentiate 9x^4 - 7x^3 + 8x^2 - 2.", "options": ["36x^3 - 21x^2 + 16x", "9x^3 - 7x^2 + 8x", "36x^2 - 21x + 16", "None"], "answer": "36x^3 - 21x^2 + 16x"},
            {"q": "Rank of matrix [[1,5],[2,4],[8,?]]?", "options": ["1", "2", "3", "None"], "answer": "2"},
            {"q": "What is the rank of the matrix [[1,2,3],[2,4,6],[3,6,9]]?", "options": ["1", "2", "3", "None of these"], "answer": "1"},
            {"q": "What is the transpose of the matrix [[1,2,3],[4,5,6]]?", "options": ["[[1,4],[2,5],[3,6]]", "[[1,2],[3,4],[5,6]]", "[[1,3],[2,4],[5,6]]", "[[1,5],[2,6],[3,4]]"], "answer": "[[1,4],[2,5],[3,6]]"}
        ]
    },
    "Data Structure using C": {
        "title": "Data Structure using C",
        "questions": [
            {"q": "What is a data structure?", "options": ["A programming language", "A way of organizing data", "A compiler", "An operating system"], "answer": "A way of organizing data"},
            {"q": "Which of the following is a primitive data structure?", "options": ["Array", "Linked List", "Integer", "Stack"], "answer": "Integer"},
            {"q": "Which is a non-primitive data structure?", "options": ["Float", "Character", "Array", "Boolean"], "answer": "Array"},
            {"q": "Which data structure stores elements in sequence?", "options": ["Tree", "Graph", "Linear Data Structure", "Non-linear Structure"], "answer": "Linear Data Structure"},
            {"q": "Which is an example of a non-linear data structure?", "options": ["Array", "Stack", "Tree", "Queue"], "answer": "Tree"},
            {"q": "Which operation accesses each element exactly once?", "options": ["Searching", "Traversing", "Sorting", "Merging"], "answer": "Traversing"},
            {"q": "What is searching in data structures?", "options": ["Deleting elements", "Finding location of an element", "Sorting elements", "Adding elements"], "answer": "Finding location of an element"},
            {"q": "Which operation arranges data in order?", "options": ["Searching", "Sorting", "Traversing", "Merging"], "answer": "Sorting"},
            {"q": "Which operation combines two sorted lists?", "options": ["Sorting", "Merging", "Searching", "Traversing"], "answer": "Merging"},
            {"q": "Which control structure executes instructions in order?", "options": ["Selection", "Iteration", "Sequential", "Loop"], "answer": "Sequential"},
            {"q": "What is recursion?", "options": ["Looping", "Function calling itself", "Sorting method", "Searching method"], "answer": "Function calling itself"},
            {"q": "What is a linear array?", "options": ["Different type elements", "Single element", "Homogeneous elements", "No elements"], "answer": "Homogeneous elements"},
            {"q": "Formula to find number of elements in array?", "options": ["UB+LB", "UB-LB+1", "UB-LB", "LB-UB"], "answer": "UB-LB+1"},
            {"q": "What is a sparse matrix?", "options": ["Matrix with all values", "Matrix with many zeros", "Matrix with only ones", "Matrix with negatives"], "answer": "Matrix with many zeros"},
            {"q": "In lower triangular matrix, non-zero elements are?", "options": ["Above diagonal", "Below diagonal", "Random", "All positions"], "answer": "Below diagonal"},
            {"q": "Which search requires sorted data?", "options": ["Linear Search", "Binary Search", "Traversal", "Sorting"], "answer": "Binary Search"},
            {"q": "Which is faster search technique?", "options": ["Linear Search", "Binary Search", "Traversal", "Sorting"], "answer": "Binary Search"},
            {"q": "Which function allocates memory at runtime?", "options": ["printf()", "malloc()", "scanf()", "main()"], "answer": "malloc()"},
            {"q": "What is a linked list?", "options": ["Contiguous storage", "Non-contiguous storage", "Only numbers", "Only characters"], "answer": "Non-contiguous storage"},
            {"q": "Which list connects last node to first?", "options": ["Singly linked list", "Doubly linked list", "Circular linked list", "Array"], "answer": "Circular linked list"}
        ]
    },
    "Python Programming": {
        "title": "Python Programming",
        "questions": [
            {"q": "Who developed Python programming language?", "options": ["Dennis Ritchie", "Guido van Rossum", "James Gosling", "Bjarne Stroustrup"], "answer": "Guido van Rossum"},
            {"q": "Which symbol is used for comments in Python?", "options": ["//", "/* */", "#", ""], "answer": "#"},
            {"q": "Which keyword is used to define a function in Python?", "options": ["func", "def", "function", "lambda"], "answer": "def"},
            {"q": "What is the correct way to output text in Python?", "options": ["printf()", "print()", "System.out.print()", "echo"], "answer": "print()"},
            {"q": "Which of the following data types is mutable in Python?", "options": ["tuple", "string", "list", "int"], "answer": "list"},
            {"q": "Which collection is ordered, changeable, and does not allow duplicate members?", "options": ["List", "Tuple", "Set", "Dictionary"], "answer": "Dictionary"},
            {"q": "How do you insert an element at a specific index in a Python list?", "options": ["append()", "insert()", "add()", "push()"], "answer": "insert()"},
            {"q": "What does len() function do?", "options": ["Calculates string weight", "Returns the number of items in an object", "Generates random numbers", "Clears a list"], "answer": "Returns the number of items in an object"},
            {"q": "Which operator is used for exponentiation (power) in Python?", "options": ["^", "**", "pow", "//"], "answer": "**"},
            {"q": "What is the output of floor division operator (//)?", "options": ["Always float", "Returns remainder", "Divides and rounds down to nearest whole number", "Complex number"], "answer": "Divides and rounds down to nearest whole number"},
            {"q": "Which block handles execution when no exceptions occur in try-except?", "options": ["else", "finally", "catch", "raise"], "answer": "else"},
            {"q": "Which keyword is used to create a loop that iterates over a sequence?", "options": ["while", "for", "do", "foreach"], "answer": "for"},
            {"q": "What is the default return value of a function that doesn't return anything explicitly?", "options": ["0", "False", "None", "Null"], "answer": "None"},
            {"q": "How do you start a conditional block in Python?", "options": ["if condition:", "if (condition) {", "if condition then", "case condition:"], "answer": "if condition:"},
            {"q": "Which string method removes whitespace from both ends?", "options": ["clean()", "strip()", "trim()", "replace()"], "answer": "strip()"},
            {"q": "Which statement can break out of a loop completely?", "options": ["continue", "break", "pass", "exit"], "answer": "break"},
            {"q": "What data type is the result of input() by default?", "options": ["int", "float", "string", "boolean"], "answer": "string"},
            {"q": "How do you convert a variable 'x' to an integer data type?", "options": ["int(x)", "str(x)", "float(x)", "cast(x)"], "answer": "int(x)"},
            {"q": "Which library is used for data manipulation and analysis?", "options": ["Math", "Pandas", "Random", "Os"], "answer": "Pandas"},
            {"q": "Which keyword is used to import modules into a program?", "options": ["include", "require", "import", "using"], "answer": "import"}
        ]
    },
    "Object Oriented Programming with JAVA": {
        "title": "Object Oriented Programming with JAVA",
        "questions": [
            {"q": "What is Object-Oriented Programming (OOP)?", "options": ["Programming with functions", "Programming using objects", "Programming using loops", "Programming using variables"], "answer": "Programming using objects"},
            {"q": "What is an object in Java?", "options": ["A function", "A variable", "An instance of a class", "A keyword"], "answer": "An instance of a class"},
            {"q": "What is a class in Java?", "options": ["A function", "A user-defined data type", "A loop", "An operator"], "answer": "A user-defined data type"},
            {"q": "What does encapsulation mean?", "options": ["Data separation", "Wrapping data and methods together", "Deleting data", "Copying data"], "answer": "Wrapping data and methods together"},
            {"q": "What is data hiding?", "options": ["Showing data", "Restricting access to data", "Deleting data", "Copying data"], "answer": "Restricting access to data"},
            {"q": "What is inheritance?", "options": ["Copying variables", "Acquiring properties of another class", "Deleting class", "Hiding data"], "answer": "Acquiring properties of another class"},
            {"q": "What is polymorphism?", "options": ["Single form", "Many forms", "No form", "Static form"], "answer": "Many forms"},
            {"q": "What is dynamic binding?", "options": ["Compile-time linking", "Runtime linking of method calls", "Static linking", "No linking"], "answer": "Runtime linking of method calls"},
            {"q": "What is message passing?", "options": ["Sending data between objects", "Printing output", "Compiling code", "Debugging code"], "answer": "Sending data between objects"},
            {"q": "Which approach does OOP follow?", "options": ["Top-down", "Bottom-up", "Linear", "Sequential"], "answer": "Bottom-up"},
            {"q": "Which language is a pure object-oriented language?", "options": ["C", "C++", "Java", "Assembly"], "answer": "Java"},
            {"q": "Which feature improves code reusability?", "options": ["Encapsulation", "Inheritance", "Abstraction", "Polymorphism"], "answer": "Inheritance"},
            {"q": "What is abstraction?", "options": ["Showing full details", "Hiding unnecessary details", "Deleting data", "Copying data"], "answer": "Hiding unnecessary details"},
            {"q": "Which keyword defines a class in Java?", "options": ["define", "class", "struct", "object"], "answer": "class"},
            {"q": "What is the starting point of a Java program?", "options": ["start()", "init()", "main()", "run()"], "answer": "main()"},
            {"q": "Which method is used to print output in Java?", "options": ["print()", "System.out.println()", "echo()", "display()"], "answer": "System.out.println()"},
            {"q": "Which of the following is NOT a Java feature?", "options": ["Platform independent", "Secure", "Pointer-based", "Object-oriented"], "answer": "Pointer-based"},
            {"q": "Java programs are compiled into?", "options": ["Machine code", "Bytecode", "Assembly code", "Binary"], "answer": "Bytecode"},
            {"q": "Which tool is used to compile Java code?", "options": ["java", "javac", "jdb", "javadoc"], "answer": "javac"},
            {"q": "Which concept allows objects to communicate?", "options": ["Inheritance", "Encapsulation", "Message passing", "Abstraction"], "answer": "Message passing"}
        ]
    },
    "Discrete Mathematical Structures": {
        "title": "Discrete Mathematical Structures",
        "questions": [
            {"q": "What is a proposition in discrete mathematics?", "options": ["A question", "A statement with truth value", "A number", "An equation"], "answer": "A statement with truth value"},
            {"q": "Which of the following is a logical connective?", "options": ["+", "-", "AND", "="], "answer": "AND"},
            {"q": "What does the symbol ∧ represent?", "options": ["OR", "AND", "NOT", "IMPLIES"], "answer": "AND"},
            {"q": "What does the symbol ∨ represent?", "options": ["AND", "OR", "NOT", "EQUAL"], "answer": "OR"},
            {"q": "Which statement is true if both operands are true?", "options": ["OR", "NOT", "AND", "IMPLIES"], "answer": "AND"},
            {"q": "What is a tautology?", "options": ["Always false", "Always true", "Sometimes true", "Undefined"], "answer": "Always true"},
            {"q": "What is a contradiction?", "options": ["Always true", "Always false", "Sometimes true", "Conditional"], "answer": "Always false"},
            {"q": "Which quantifier means 'for all'?", "options": ["∃", "∀", "∈", "⊂"], "answer": "∀"},
            {"q": "Which quantifier means 'there exists'?", "options": ["∀", "∃", "⊆", "∉"], "answer": "∃"},
            {"q": "What is a set?", "options": ["Collection of elements", "Single number", "Equation", "Function"], "answer": "Collection of elements"},
            {"q": "Which symbol represents subset?", "options": ["∈", "⊆", "∪", "∩"], "answer": "⊆"},
            {"q": "What does ∪ represent in sets?", "options": ["Intersection", "Union", "Difference", "Subset"], "answer": "Union"},
            {"q": "What does ∩ represent in sets?", "options": ["Union", "Intersection", "Difference", "Complement"], "answer": "Intersection"},
            {"q": "What is a function?", "options": ["Relation between inputs and outputs", "Only numbers", "Set of variables", "Equation"], "answer": "Relation between inputs and outputs"},
            {"q": "What is cardinality of a set?", "options": ["Sum of elements", "Number of elements", "Difference", "Product"], "answer": "Number of elements"},
            {"q": "What is recursion?", "options": ["Looping", "Function calling itself", "Sorting method", "Searching method"], "answer": "Function calling itself"},
            {"q": "Which method proves statements for all natural numbers?", "options": ["Induction", "Contradiction", "Direct proof", "Algorithm"], "answer": "Induction"},
            {"q": "What is an algorithm?", "options": ["Random steps", "Step-by-step procedure", "Equation", "Formula"], "answer": "Step-by-step procedure"},
            {"q": "What does Big-O notation represent?", "options": ["Exact time", "Memory size", "Growth rate of function", "Loop count"], "answer": "Growth rate of function"},
            {"q": "Which topic deals with nodes and edges?", "options": ["Sets", "Graphs", "Functions", "Logic"], "answer": "Graphs"}
        ]
    },
    "Csharp": {
        "title": "C# and .NET Framework",
        "questions": [
            {"q": "Which component of .NET execution engine compiles intermediate code into machine code?", "options": ["CLR", "JIT Compiler", "Garbage Collector", "MSIL"], "answer": "JIT Compiler"},
            {"q": "What is the correct root class of all types in the .NET Framework sub-system?", "options": ["System.Object", "System.Type", "System.Root", "System.Class"], "answer": "System.Object"},
            {"q": "Which keyword is used in C# to prevent a class from being inherited by other classes?", "options": ["static", "abstract", "sealed", "final"], "answer": "sealed"},
            {"q": "What type of memory allocation handles struct data structures by default in C#?", "options": ["Heap memory", "Stack memory", "Garbage collection allocation", "Global data segment"], "answer": "Stack memory"},
            {"q": "Which of the following describes the nature of an Interface in C# explicitly?", "options": ["Reference Type", "Value Type", "Pointer Type", "Static Type"], "answer": "Reference Type"},
            {"q": "Which symbol is used to initiate string interpolation format syntax in C#?", "options": ["@", "#", "$", "%"], "answer": "$"},
            {"q": "What is the primary function of the Garbage Collector in .NET environments?", "options": ["To compile MSIL to Native code", "To automate dynamic memory management", "To enforce application type safety", "To link external assemblies"], "answer": "To automate dynamic memory management"},
            {"q": "Which design pattern keyword handles asynchronous method signatures in modern C#?", "options": ["thread / join", "async / await", "defer / resume", "task / start"], "answer": "async / await"},
            {"q": "Which of these operators checks compatibility safely and returns null if a conversion fails?", "options": ["is", "as", "cast", "convert"], "answer": "as"},
            {"q": "What architecture collection enables uniform data queries from diverse databases natively in C#?", "options": ["ADO.NET", "LINQ", "WCF", "Entity Framework"], "answer": "LINQ"},
            {"q": "Which data structure storage representation is explicitly mutable in C# operations?", "options": ["System.String", "System.Text.StringBuilder", "System.Tuple", "Anonymous Types"], "answer": "System.Text.StringBuilder"},
            {"q": "What keyword explicitly allows a derived method instance to override base implementation structures?", "options": ["new", "abstract", "override", "virtual"], "answer": "override"},
            {"q": "Which execution block guarantees implementation operations execute regardless of code exceptions?", "options": ["try", "catch", "finally", "throw"], "answer": "finally"},
            {"q": "What intermediate system form is your human-readable C# source compiled down to initially?", "options": ["Native Machine Code", "Assembly Manifest Bytecode", "Microsoft Intermediate Language (MSIL)", "Binary Stream Objects"], "answer": "Microsoft Intermediate Language (MSIL)"},
            {"q": "Which keyword represents a parameter layout structure passed explicitly by reference constraints?", "options": ["out", "ref", "in", "params"], "answer": "ref"},
            {"q": "What access modifier constrains internal structural visibility uniquely to its declaring class target?", "options": ["public", "protected", "private", "internal"], "answer": "private"},
            {"q": "What process structure safely packages a structural value type directly into an objective object scope?", "options": ["Unboxing", "Boxing", "Casting", "Parsing"], "answer": "Boxing"},
            {"q": "Which generic class collection provides unique fast Key-Value paired entity mapping lookups?", "options": ["List<T>", "Dictionary<TKey, TValue>", "HashSet<T>", "Queue<T>"], "answer": "Dictionary<TKey, TValue>"},
            {"q": "What structural tracking attribute context safely declares unmanaged pointer arithmetic contexts?", "options": ["unsafe", "fixed", "volatile", "checked"], "answer": "unsafe"},
            {"q": "Which configuration file handles base routing endpoints and settings in core framework deployments?", "options": ["app.config / web.config", "package.json", "settings.py", "manifest.xml"], "answer": "app.config / web.config"}
        ]
    },
    "Database Management Systems": {
        "title": "Database Management Systems",
        "questions": [
            {"q": "What does DBMS stand for?", "options": ["Data Backup Management System", "Database Management System", "Data Basic Management System", "Database Method System"], "answer": "Database Management System"},
            {"q": "Which language is used to access databases?", "options": ["HTML", "SQL", "C++", "Java"], "answer": "SQL"},
            {"q": "Which key uniquely identifies a record?", "options": ["Foreign Key", "Primary Key", "Candidate Key", "Super Key"], "answer": "Primary Key"},
            {"q": "Which normal form removes partial dependency?", "options": ["1NF", "2NF", "3NF", "BCNF"], "answer": "2NF"},
            {"q": "What is a tuple in DBMS?", "options": ["Column", "Row", "Table", "Database"], "answer": "Row"},
            {"q": "Which command is used to retrieve data?", "options": ["INSERT", "UPDATE", "SELECT", "DELETE"], "answer": "SELECT"},
            {"q": "Which key is used to link two tables?", "options": ["Primary Key", "Foreign Key", "Candidate Key", "Unique Key"], "answer": "Foreign Key"},
            {"q": "What is normalization?", "options": ["Data duplication", "Data organization", "Data deletion", "Data encryption"], "answer": "Data organization"},
            {"q": "Which normal form removes transitive dependency?", "options": ["1NF", "2NF", "3NF", "4NF"], "answer": "3NF"},
            {"q": "Which operation removes records?", "options": ["INSERT", "UPDATE", "DELETE", "SELECT"], "answer": "DELETE"},
            {"q": "What is a database?", "options": ["Collection of programs", "Collection of data", "Collection of queries", "Collection of keys"], "answer": "Collection of data"},
            {"q": "Which SQL clause is used to filter records?", "options": ["ORDER BY", "GROUP BY", "WHERE", "HAVING"], "answer": "WHERE"},
            {"q": "Which constraint ensures uniqueness?", "options": ["NOT NULL", "UNIQUE", "DEFAULT", "CHECK"], "answer": "UNIQUE"},
            {"q": "Which command adds new records?", "options": ["INSERT", "DELETE", "UPDATE", "SELECT"], "answer": "INSERT"},
            {"q": "Which join returns all records from both tables?", "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"], "answer": "FULL JOIN"},
            {"q": "What is a relation in DBMS?", "options": ["Row", "Column", "Table", "Key"], "answer": "Table"},
            {"q": "Which SQL keyword sorts the result?", "options": ["SORT BY", "ORDER BY", "GROUP BY", "ARRANGE"], "answer": "ORDER BY"},
            {"q": "Which model uses tables?", "options": ["Hierarchical", "Network", "Relational", "Object"], "answer": "Relational"},
            {"q": "What is an attribute?", "options": ["Row", "Column", "Table", "Database"], "answer": "Column"},
            {"q": "Which constraint prevents null values?", "options": ["UNIQUE", "CHECK", "NOT NULL", "DEFAULT"], "answer": "NOT NULL"}
        ]
    },
    "Computer Communication and Networks": {
        "title": "Computer Communication and Networks",
        "questions": [
            {"q": "What does LAN stand for?", "options": ["Large Area Network", "Local Area Network", "Long Area Network", "Light Area Network"], "answer": "Local Area Network"},
            {"q": "Which device connects multiple networks?", "options": ["Switch", "Router", "Hub", "Bridge"], "answer": "Router"},
            {"q": "What is the full form of IP?", "options": ["Internet Protocol", "Internal Protocol", "Interconnect Protocol", "Internet Process"], "answer": "Internet Protocol"},
            {"q": "Which layer is responsible for data encryption?", "options": ["Network Layer", "Presentation Layer", "Transport Layer", "Application Layer"], "answer": "Presentation Layer"},
            {"q": "Which topology uses a central hub?", "options": ["Bus", "Ring", "Star", "Mesh"], "answer": "Star"},
            {"q": "What does HTTP stand for?", "options": ["Hyper Text Transfer Protocol", "High Transfer Text Protocol", "Hyperlink Transfer Protocol", "Home Transfer Text Protocol"], "answer": "Hyper Text Transfer Protocol"},
            {"q": "Which device works at Data Link layer?", "options": ["Router", "Switch", "Gateway", "Repeater"], "answer": "Switch"},
            {"q": "What is the default port for HTTP?", "options": ["21", "25", "80", "443"], "answer": "80"},
            {"q": "Which protocol is used to send emails?", "options": ["FTP", "SMTP", "HTTP", "SNMP"], "answer": "SMTP"},
            {"q": "Which layer handles routing?", "options": ["Transport", "Network", "Session", "Application"], "answer": "Network"},
            {"q": "What is the full form of DNS?", "options": ["Domain Name System", "Data Name System", "Domain Network Service", "Dynamic Name System"], "answer": "Domain Name System"},
            {"q": "Which topology has a closed loop?", "options": ["Star", "Bus", "Ring", "Mesh"], "answer": "Ring"},
            {"q": "Which protocol is used for file transfer?", "options": ["FTP", "HTTP", "SMTP", "SNMP"], "answer": "FTP"},
            {"q": "What is the function of a repeater?", "options": ["Filter data", "Amplify signal", "Route packets", "Encrypt data"], "answer": "Amplify signal"},
            {"q": "Which layer ensures reliable delivery?", "options": ["Application", "Transport", "Network", "Physical"], "answer": "Transport"},
            {"q": "Which protocol is secure version of HTTP?", "options": ["SHTTP", "HTTPS", "FTPS", "SMTP"], "answer": "HTTPS"},
            {"q": "What is bandwidth?", "options": ["Data storage", "Transmission capacity", "Signal type", "Network device"], "answer": "Transmission capacity"},
            {"q": "Which device broadcasts data to all ports?", "options": ["Switch", "Router", "Hub", "Bridge"], "answer": "Hub"},
            {"q": "Which layer is closest to the user?", "options": ["Physical", "Network", "Application", "Data Link"], "answer": "Application"},
            {"q": "Which protocol assigns IP addresses automatically?", "options": ["DNS", "DHCP", "FTP", "HTTP"], "answer": "DHCP"}
        ]
    },
    "Computer Multimedia and Animation": {
        "title": "Computer Multimedia and Animation",
        "questions": [
            {"q": "What is multimedia?", "options": ["Only text", "Combination of text, audio, video, and images", "Only images", "Only audio"], "answer": "Combination of text, audio, video, and images"},
            {"q": "Which format is commonly used for images?", "options": ["MP3", "JPEG", "MP4", "AVI"], "answer": "JPEG"},
            {"q": "Which format is used for audio files?", "options": ["MP3", "PNG", "GIF", "BMP"], "answer": "MP3"},
            {"q": "What does GIF stand for?", "options": ["Graphics Interchange Format", "Graphical Image File", "Graphic Interface File", "General Image Format"], "answer": "Graphics Interchange Format"},
            {"q": "Which software is used for animation?", "options": ["MS Word", "Adobe Animate", "Excel", "Notepad"], "answer": "Adobe Animate"},
            {"q": "What is frame rate?", "options": ["Number of pixels", "Images per second", "Audio quality", "File size"], "answer": "Images per second"},
            {"q": "Which file format supports animation?", "options": ["JPEG", "PNG", "GIF", "TXT"], "answer": "GIF"},
            {"q": "What is resolution?", "options": ["Image clarity", "Sound level", "File size", "Animation speed"], "answer": "Image clarity"},
            {"q": "Which color model is used for screens?", "options": ["CMYK", "RGB", "HSV", "HSL"], "answer": "RGB"},
            {"q": "What does MP4 represent?", "options": ["Image format", "Video format", "Audio format", "Text format"], "answer": "Video format"},
            {"q": "Which tool is used for video editing?", "options": ["Photoshop", "Premiere Pro", "Notepad", "Excel"], "answer": "Premiere Pro"},
            {"q": "What is animation?", "options": ["Static image", "Moving images sequence", "Audio recording", "Text editing"], "answer": "Moving images sequence"},
            {"q": "Which format is lossless?", "options": ["JPEG", "PNG", "MP3", "MP4"], "answer": "PNG"},
            {"q": "What is timeline in animation?", "options": ["Color tool", "Frame sequence control", "Audio tool", "Drawing tool"], "answer": "Frame sequence control"},
            {"q": "Which is a vector graphics format?", "options": ["JPEG", "PNG", "SVG", "BMP"], "answer": "SVG"},
            {"q": "What is keyframe?", "options": ["Random frame", "Important frame defining motion", "Audio frame", "Final frame"], "answer": "Important frame defining motion"},
            {"q": "Which format is best for high-quality print?", "options": ["RGB", "CMYK", "GIF", "MP3"], "answer": "CMYK"},
            {"q": "What is rendering?", "options": ["Deleting files", "Final output creation", "Drawing shapes", "Compressing files"], "answer": "Final output creation"},
            {"q": "Which software is used for image editing?", "options": ["Photoshop", "Excel", "PowerPoint", "Notepad"], "answer": "Photoshop"},
            {"q": "What is compression?", "options": ["Increasing size", "Reducing file size", "Editing image", "Adding sound"], "answer": "Reducing file size"}
        ]
    },
    "Operating System Concepts": {
        "title": "Operating System Concepts",
        "questions": [
            {"q": "What is an operating system?", "options": ["Application software", "System software", "Utility program", "Programming language"], "answer": "System software"},
            {"q": "Which scheduling algorithm uses shortest job first?", "options": ["FCFS", "SJF", "Round Robin", "Priority"], "answer": "SJF"},
            {"q": "What is a process?", "options": ["Program in execution", "File in memory", "Hardware device", "Instruction set"], "answer": "Program in execution"},
            {"q": "Which memory is fastest?", "options": ["RAM", "ROM", "Cache", "Hard Disk"], "answer": "Cache"},
            {"q": "What is deadlock?", "options": ["Process termination", "CPU idle state", "Processes waiting indefinitely", "Memory leak"], "answer": "Processes waiting indefinitely"},
            {"q": "Which scheduling algorithm uses time slices?", "options": ["SJF", "Round Robin", "FCFS", "Priority"], "answer": "Round Robin"},
            {"q": "What is virtual memory?", "options": ["Physical memory", "Secondary memory used as RAM", "Cache memory", "Register"], "answer": "Secondary memory used as RAM"},
            {"q": "Which is not a type of OS?", "options": ["Batch", "Time-sharing", "Distributed", "Compiler"], "answer": "Compiler"},
            {"q": "What is paging?", "options": ["Memory allocation technique", "CPU scheduling", "Disk formatting", "Process creation"], "answer": "Memory allocation technique"},
            {"q": "What is a thread?", "options": ["Lightweight process", "Heavy process", "Memory block", "File system"], "answer": "Lightweight process"},
            {"q": "Which algorithm is non-preemptive?", "options": ["Round Robin", "SJF", "Priority (preemptive)", "Multilevel queue"], "answer": "SJF"},
            {"q": "What is context switching?", "options": ["Switching memory", "Switching CPU between processes", "Changing files", "Loading OS"], "answer": "Switching CPU between processes"},
            {"q": "Which OS is open-source?", "options": ["Windows", "Linux", "macOS", "DOS"], "answer": "Linux"},
            {"q": "What is thrashing?", "options": ["High CPU usage", "Excessive paging", "Process creation", "Disk failure"], "answer": "Excessive paging"},
            {"q": "Which memory is non-volatile?", "options": ["RAM", "Cache", "ROM", "Register"], "answer": "ROM"},
            {"q": "What is a semaphore?", "options": ["Memory unit", "Process synchronization tool", "Scheduling method", "File system"], "answer": "Process synchronization tool"},
            {"q": "Which scheduling algorithm is first come first serve?", "options": ["FCFS", "SJF", "Round Robin", "Priority"], "answer": "FCFS"},
            {"q": "What is starvation?", "options": ["Process completion", "Indefinite waiting", "Deadlock prevention", "CPU idle"], "answer": "Indefinite waiting"},
            {"q": "Which system call creates a process?", "options": ["exec()", "fork()", "wait()", "exit()"], "answer": "fork()"},
            {"q": "What is a file system?", "options": ["Memory manager", "Process scheduler", "Storage organization method", "CPU controller"], "answer": "Storage organization method"}
        ]
    },
    "Statistical Computing and R Programming": {
        "title": "Statistical Computing and R Programming",
        "questions": [
            {"q": "What is R?", "options": ["Database", "Programming language", "Operating system", "Compiler"], "answer": "Programming language"},
            {"q": "Which symbol is used for assignment in R?", "options": ["=", "<-", "->", ":"], "answer": "<-"},
            {"q": "Which function is used to print output in R?", "options": ["print()", "display()", "show()", "output()"], "answer": "print()"},
            {"q": "What is a vector in R?", "options": ["Single value", "Collection of elements", "Function", "Loop"], "answer": "Collection of elements"},
            {"q": "Which function creates a sequence in R?", "options": ["seq()", "rep()", "c()", "length()"], "answer": "seq()"},
            {"q": "Which data type stores true/false?", "options": ["Numeric", "Character", "Logical", "Integer"], "answer": "Logical"},
            {"q": "What does NA represent in R?", "options": ["Not Applicable", "Missing value", "New Array", "Negative value"], "answer": "Missing value"},
            {"q": "Which function reads a CSV file?", "options": ["read.csv()", "scan()", "load()", "input()"], "answer": "read.csv()"},
            {"q": "Which function gives summary statistics?", "options": ["mean()", "summary()", "sd()", "var()"], "answer": "summary()"},
            {"q": "Which loop is used in R?", "options": ["for", "while", "repeat", "All of the above"], "answer": "All of the above"},
            {"q": "What is a data frame?", "options": ["Single value", "2D table", "Vector", "List"], "answer": "2D table"},
            {"q": "Which function combines elements into a vector?", "options": ["c()", "combine()", "merge()", "append()"], "answer": "c()"},
            {"q": "Which function calculates mean?", "options": ["avg()", "mean()", "median()", "sum()"], "answer": "mean()"},
            {"q": "Which package is used for plotting?", "options": ["ggplot2", "dplyr", "tidyr", "readr"], "answer": "ggplot2"},
            {"q": "What is indexing in R?", "options": ["Looping", "Accessing elements", "Printing data", "Deleting data"], "answer": "Accessing elements"},
            {"q": "Which operator is used for comparison?", "options": ["==", "<-", "=", "::"], "answer": "=="},
            {"q": "Which function repeats values?", "options": ["rep()", "seq()", "c()", "repeat()"], "answer": "rep()"},
            {"q": "Which function gives length of vector?", "options": ["size()", "count()", "length()", "dim()"], "answer": "length()"},
            {"q": "What is a list in R?", "options": ["Single element", "Same type elements", "Different type elements", "Loop"], "answer": "Different type elements"},
            {"q": "Which function installs packages?", "options": ["install.packages()", "library()", "require()", "add.packages()"], "answer": "install.packages()"}
        ]
    },
    "Design and Analysis of Algorithms": {
        "title": "Design and Analysis of Algorithms",
        "questions": [
            {"q": "What is the time complexity of binary search?", "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"], "answer": "O(log n)"},
            {"q": "Which algorithm uses divide and conquer?", "options": ["Bubble Sort", "Merge Sort", "Selection Sort", "Insertion Sort"], "answer": "Merge Sort"},
            {"q": "What is the worst-case time complexity of quicksort?", "options": ["O(n)", "O(log n)", "O(n log n)", "O(n^2)"], "answer": "O(n^2)"},
            {"q": "Which notation represents upper bound?", "options": ["Omega (Ω)", "Theta (Θ)", "Big O (O)", "Sigma (Σ)"], "answer": "Big O (O)"},
            {"q": "Which algorithm is greedy?", "options": ["Dijkstra", "Merge Sort", "Binary Search", "DFS"], "answer": "Dijkstra"},
            {"q": "Which algorithm finds minimum spanning tree?", "options": ["Prim", "DFS", "BFS", "Binary Search"], "answer": "Prim"},
            {"q": "What is the space complexity?", "options": ["Time used", "Memory used", "CPU cycles", "Disk usage"], "answer": "Memory used"},
            {"q": "Which sorting algorithm is stable?", "options": ["Quick Sort", "Heap Sort", "Merge Sort", "Selection Sort"], "answer": "Merge Sort"},
            {"q": "What is recurrence relation?", "options": ["Sorting method", "Function defined recursively", "Search method", "Graph algorithm"], "answer": "Function defined recursively"},
            {"q": "Which algorithm uses dynamic programming?", "options": ["Floyd-Warshall", "DFS", "BFS", "Insertion Sort"], "answer": "Floyd-Warshall"},
            {"q": "What is the best-case time of insertion sort?", "options": ["O(n)", "O(n^2)", "O(log n)", "O(1)"], "answer": "O(n)"},
            {"q": "Which problem uses backtracking?", "options": ["N-Queens", "Binary Search", "Merge Sort", "Dijkstra"], "answer": "N-Queens"},
            {"q": "Which traversal uses queue?", "options": ["DFS", "BFS", "Preorder", "Postorder"], "answer": "BFS"},
            {"q": "Which traversal uses stack?", "options": ["BFS", "DFS", "Level Order", "Binary Search"], "answer": "DFS"},
            {"q": "Which algorithm is used for shortest path?", "options": ["Kruskal", "Dijkstra", "Prim", "Merge Sort"], "answer": "Dijkstra"},
            {"q": "What is brute force method?", "options": ["Optimal approach", "Trial and error method", "Greedy method", "Divide and conquer"], "answer": "Trial and error method"},
            {"q": "Which sorting has O(n^2) average case?", "options": ["Quick Sort", "Merge Sort", "Bubble Sort", "Heap Sort"], "answer": "Bubble Sort"},
            {"q": "Which algorithm is used for MST?", "options": ["Prim", "Dijkstra", "DFS", "BFS"], "answer": "Prim"},
            {"q": "What is asymptotic analysis?", "options": ["Exact time", "Approximate behavior", "Memory allocation", "CPU usage"], "answer": "Approximate behavior"},
            {"q": "Which technique solves overlapping subproblems?", "options": ["Greedy", "Dynamic Programming", "Divide and Conquer", "Backtracking"], "answer": "Dynamic Programming"}
        ]
    },
    "Software Engineering": {
        "title": "Software Engineering",
        "questions": [
            {"q": "What is software engineering?", "options": ["Hardware design", "Systematic software development", "Network setup", "Database management"], "answer": "Systematic software development"},
            {"q": "Which model is linear sequential?", "options": ["Agile", "Spiral", "Waterfall", "RAD"], "answer": "Waterfall"},
            {"q": "What is SDLC?", "options": ["Software Development Life Cycle", "System Design Logic Code", "Software Data Link Control", "System Development Logic Cycle"], "answer": "Software Development Life Cycle"},
            {"q": "Which phase gathers requirements?", "options": ["Design", "Testing", "Requirement Analysis", "Maintenance"], "answer": "Requirement Analysis"},
            {"q": "Which model is iterative?", "options": ["Waterfall", "Agile", "V-Model", "Big Bang"], "answer": "Agile"},
            {"q": "What is debugging?", "options": ["Writing code", "Fixing errors", "Testing software", "Designing system"], "answer": "Fixing errors"},
            {"q": "Which testing checks individual units?", "options": ["Integration Testing", "System Testing", "Unit Testing", "Acceptance Testing"], "answer": "Unit Testing"},
            {"q": "What is a bug?", "options": ["Feature", "Error", "Requirement", "Design"], "answer": "Error"},
            {"q": "Which document defines requirements?", "options": ["SRS", "SDD", "Test Plan", "Code"], "answer": "SRS"},
            {"q": "What is maintenance?", "options": ["Developing software", "Fixing and updating software", "Testing software", "Designing UI"], "answer": "Fixing and updating software"},
            {"q": "Which model focuses on risk analysis?", "options": ["Waterfall", "Spiral", "Agile", "RAD"], "answer": "Spiral"},
            {"q": "What is version control?", "options": ["Code execution", "Tracking changes", "Testing code", "Debugging"], "answer": "Tracking changes"},
            {"q": "Which testing is done by users?", "options": ["Unit Testing", "Integration Testing", "Acceptance Testing", "System Testing"], "answer": "Acceptance Testing"},
            {"q": "What is a prototype?", "options": ["Final product", "Initial model", "Bug report", "Test case"], "answer": "Initial model"},
            {"q": "Which phase comes after design?", "options": ["Testing", "Coding", "Maintenance", "Requirement"], "answer": "Coding"},
            {"q": "What is cohesion?", "options": ["Module independence", "Module strength", "Code duplication", "Data flow"], "answer": "Module strength"},
            {"q": "What is coupling?", "options": ["Module independence", "Dependency between modules", "Testing method", "Design phase"], "answer": "Dependency between modules"},
            {"q": "Which diagram shows system structure?", "options": ["Flowchart", "UML Diagram", "ER Diagram", "DFD"], "answer": "UML Diagram"},
            {"q": "What is validation?", "options": ["Building product right", "Building right product", "Testing code", "Fixing bugs"], "answer": "Building right product"},
            {"q": "What is verification?", "options": ["Building right product", "Building product right", "Testing users", "Debugging"], "answer": "Building product right"}
        ]
    },
    "Hypertext preprocessor": {
        "title": "Hypertext preprocessor",
        "questions": [
            {"q": "What does PHP stand for?", "options": ["Personal Home Page", "Hypertext Preprocessor", "Private Home Page", "Preprocessed Hypertext"], "answer": "Hypertext Preprocessor"},
            {"q": "PHP is a ___ language?", "options": ["Client-side", "Server-side", "Markup", "Database"], "answer": "Server-side"},
            {"q": "Which symbol is used for variables in PHP?", "options": ["#", "$", "@", "%"], "answer": "$"},
            {"q": "Which function outputs text?", "options": ["print()", "echo()", "display()", "show()"], "answer": "echo()"},
            {"q": "Which file extension is used for PHP?", "options": [".html", ".php", ".js", ".css"], "answer": ".php"},
            {"q": "Which superglobal stores form data?", "options": ["$_GET", "$_POST", "$_REQUEST", "All of the above"], "answer": "All of the above"},
            {"q": "Which operator is used for concatenation?", "options": ["+", ".", "&", "*"], "answer": "."},
            {"q": "Which function starts a session?", "options": ["start_session()", "session_start()", "begin_session()", "init_session()"], "answer": "session_start()"},
            {"q": "Which function is used to include files?", "options": ["include()", "require()", "Both include() and require()", "import()"], "answer": "Both include() and require()"},
            {"q": "Which method is more secure for form data?", "options": ["GET", "POST", "REQUEST", "SESSION"], "answer": "POST"},
            {"q": "Which symbol is used for comments?", "options": ["//", "#", "/* */", "All of the above"], "answer": "All of the above"},
            {"q": "Which function is used to count array elements?", "options": ["count()", "size()", "length()", "total()"], "answer": "count()"},
            {"q": "Which function is used to connect MySQL?", "options": ["connect_db()", "mysqli_connect()", "db_connect()", "mysql_open()"], "answer": "mysqli_connect()"},
            {"q": "Which loop is used in PHP?", "options": ["for", "while", "foreach", "All of the above"], "answer": "All of the above"},
            {"q": "Which keyword defines a function?", "options": ["func", "function", "define", "method"], "answer": "function"},
            {"q": "Which array stores multiple values?", "options": ["Indexed array", "Associative array", "Multidimensional array", "All of the above"], "answer": "All of the above"},
            {"q": "Which function ends script execution?", "options": ["stop()", "exit()", "end()", "break()"], "answer": "exit()"},
            {"q": "Which variable stores session data?", "options": ["$_SESSION", "$_COOKIE", "$_SERVER", "$_ENV"], "answer": "$_SESSION"},
            {"q": "Which function deletes a cookie?", "options": ["delete_cookie()", "unset()", "setcookie()", "remove_cookie()"], "answer": "setcookie()"},
            {"q": "Which function checks variable type?", "options": ["type()", "gettype()", "var_type()", "checktype()"], "answer": "gettype()"}
        ]
    },
    "Web Content Management System": {
        "title": "Web Content Management System",
        "questions": [
            {"q": "What does WCMS stand for?", "options": ["Web Content Management System", "Website Control Management System", "Web Code Management System", "Web Content Monitoring System"], "answer": "Web Content Management System"},
            {"q": "What is the main purpose of WCMS?", "options": ["Design hardware", "Manage web content", "Develop OS", "Create databases"], "answer": "Manage web content"},
            {"q": "Which is an example of WCMS?", "options": ["Windows", "Linux", "WordPress", "MySQL"], "answer": "WordPress"},
            {"q": "Which language is commonly used in WCMS?", "options": ["HTML", "CSS", "PHP", "All of the above"], "answer": "All of the above"},
            {"q": "What is a CMS?", "options": ["Content Management System", "Control Management System", "Computer Management System", "Central Management System"], "answer": "Content Management System"},
            {"q": "Which role manages content in WCMS?", "options": ["Editor", "Admin", "Author", "All of the above"], "answer": "All of the above"},
            {"q": "What is a plugin?", "options": ["Core file", "Extension", "Theme", "Database"], "answer": "Extension"},
            {"q": "What is a theme?", "options": ["Functionality", "Design template", "Database", "Plugin"], "answer": "Design template"},
            {"q": "Which database is commonly used with WCMS?", "options": ["Oracle", "MySQL", "MongoDB", "SQLite"], "answer": "MySQL"},
            {"q": "What is SEO?", "options": ["Search Engine Optimization", "System Engine Operation", "Software Execution Output", "Search Engine Operation"], "answer": "Search Engine Optimization"},
            {"q": "Which is open-source CMS?", "options": ["WordPress", "Joomla", "Drupal", "All of the above"], "answer": "All of the above"},
            {"q": "What is a dashboard?", "options": ["Front-end page", "Admin interface", "Database table", "Plugin"], "answer": "Admin interface"},
            {"q": "What is content publishing?", "options": ["Deleting content", "Making content live", "Editing content", "Saving content"], "answer": "Making content live"},
            {"q": "What is a widget?", "options": ["Small block element", "Database table", "Theme", "Plugin"], "answer": "Small block element"},
            {"q": "Which protocol is used in web?", "options": ["FTP", "HTTP", "SMTP", "All of the above"], "answer": "All of the above"},
            {"q": "What is version control?", "options": ["Tracking changes", "Deleting files", "Editing images", "Hosting website"], "answer": "Tracking changes"},
            {"q": "What is web hosting?", "options": ["Storing website online", "Designing pages", "Writing code", "Testing website"], "answer": "Storing website online"},
            {"q": "What is responsive design?", "options": ["Fixed layout", "Adapts to devices", "Static page", "Only desktop view"], "answer": "Adapts to devices"},
            {"q": "Which role has full control?", "options": ["Editor", "Author", "Admin", "Subscriber"], "answer": "Admin"},
            {"q": "What is content editing?", "options": ["Deleting data", "Modifying content", "Uploading files", "Designing UI"], "answer": "Modifying content"}
        ]
    },
    "J2EE": {
        "title": "J2EE",
        "questions": [
            {"q": "What is Java?", "options": ["Programming language", "Database", "Operating system", "Browser"], "answer": "Programming language"},
            {"q": "What does JVM stand for?", "options": ["Java Virtual Machine", "Java Variable Method", "Joint Virtual Memory", "Java Verified Machine"], "answer": "Java Virtual Machine"},
            {"q": "Which component handles business logic in MVC?", "options": ["Model", "View", "Controller", "Servlet"], "answer": "Model"},
            {"q": "Which component handles user interface in MVC?", "options": ["Model", "View", "Controller", "Bean"], "answer": "View"},
            {"q": "Which component controls flow in MVC?", "options": ["Model", "View", "Controller", "JSP"], "answer": "Controller"},
            {"q": "Which package contains Servlet classes?", "options": ["java.io", "javax.servlet", "java.util", "java.net"], "answer": "javax.servlet"},
            {"q": "Which technology is used for dynamic web pages?", "options": ["HTML", "JSP", "CSS", "XML"], "answer": "JSP"},
            {"q": "What is a Servlet?", "options": ["Database", "Server-side program", "Client app", "Framework"], "answer": "Server-side program"},
            {"q": "Which method handles GET request?", "options": ["doPost()", "doGet()", "service()", "init()"], "answer": "doGet()"},
            {"q": "Which method handles POST request?", "options": ["doGet()", "doPost()", "destroy()", "init()"], "answer": "doPost()"},
            {"q": "Which file configures web app?", "options": ["web.xml", "config.xml", "app.xml", "server.xml"], "answer": "web.xml"},
            {"q": "What is JDBC?", "options": ["Java Database Connectivity", "Java Data Control", "Java Dynamic Code", "Java Database Control"], "answer": "Java Database Connectivity"},
            {"q": "Which driver connects Java to database?", "options": ["ODBC", "JDBC Driver", "HTTP Driver", "FTP Driver"], "answer": "JDBC Driver"},
            {"q": "Which statement executes SQL?", "options": ["executeQuery()", "runSQL()", "executeSQL()", "queryRun()"], "answer": "executeQuery()"},
            {"q": "What is J2EE?", "options": ["Java 2 Enterprise Edition", "Java 2 Easy Edition", "Java Enterprise Engine", "Java Execution Edition"], "answer": "Java 2 Enterprise Edition"},
            {"q": "Which object stores request data?", "options": ["response", "request", "session", "context"], "answer": "request"},
            {"q": "Which object sends response?", "options": ["request", "response", "session", "config"], "answer": "response"},
            {"q": "What is session?", "options": ["Single request", "User interaction tracking", "Database table", "Servlet method"], "answer": "User interaction tracking"},
            {"q": "Which tag is used in JSP?", "options": ["<jsp:useBean>", "<html>", "<css>", "<script>"], "answer": "<jsp:useBean>"},
            {"q": "Which architecture separates concerns?", "options": ["MVC", "Client-server", "Peer-to-peer", "Monolithic"], "answer": "MVC"}
        ]
    }
}

# --- 3. ROUTES ---

@app.route('/')
def home():
    if 'user' not in session: 
        return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            error = "Invalid Username or Password"
            
    return render_template('login page.html', error=error)

@app.route('/library')
def library():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('library.html', items=LIBRARY_BOOKS)

@app.route('/study-materials')
def materials():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('materials.html', items=STUDY_MATERIALS)

@app.route('/quizzes')
def quizzes():
    if 'user' not in session: return redirect(url_for('login'))
    q_list = [{"id": k, "title": v["title"]} for k, v in QUIZ_DATA.items()]
    return render_template('quiz_list.html', quizzes=q_list)

@app.route('/quiz/<quiz_id>')
def start_quiz(quiz_id):
    if 'user' not in session: return redirect(url_for('login'))
    quiz = QUIZ_DATA.get(quiz_id)
    if not quiz: return redirect(url_for('quizzes'))
    return render_template('quiz.html', quiz=quiz, quiz_id=quiz_id)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'user' not in session: return redirect(url_for('login'))
    
    quiz_id = request.form.get('quiz_id')
    quiz = QUIZ_DATA.get(quiz_id)
    questions = quiz["questions"]
    
    score = 0
    detailed_results = []
    
    for i, q in enumerate(questions):
        user_ans = request.form.get(f'q{i}')
        is_correct = (user_ans == q["answer"])
        if is_correct:
            score += 1
        
        detailed_results.append({
            "question": q["q"],
            "user_answer": user_ans,
            "correct_answer": q["answer"],
            "is_correct": is_correct
        })

    # Save to Supabase PostgreSQL database instead of CSV
    new_result = QuizResult(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        user=session['user'],
        quiz=quiz_id,
        score=score,
        total=len(questions)
    )
    db.session.add(new_result)
    db.session.commit()

    return render_template('results.html', 
                           score=score, 
                           total=len(questions), 
                           details=detailed_results,
                           quiz_title=quiz["title"])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
