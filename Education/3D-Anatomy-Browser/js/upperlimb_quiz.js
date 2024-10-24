const quizData = [
  {
    question: "Name structure number 1",
    options: ["M. subscapularis", "M. supraspinatus", "M. teres minor ", "M. infraspinatus", "M. deltoideus", "M. teres major", "M. latissimus dorsi"],
    answer: "M. teres major"
  },
  {
    question: "Which insertion of structure 2 is correct?",
    options: ["Tuberculum minus", "tuberculum majus", "tuberculum infraglenoidale", "crista tuberculi minoris", "crista tuberculi majoris"],
    answer: "crista tuberculi minoris"
  },
  {
    question: "Which nerve innervates structure 3?",
    options: ["n. dorsalis scapulae", "n. subscapularis", "n. suprascapularis", "n. infrascapularis", "n. thoracicus longus", "n. pectoralis lateralis"],
    answer: "n. suprascapularis"
  },
  {
    question: "Which origin of structure 4 is incorrect?",
    options: ["Transverse processes of the thoracic vertebrae", "Spinous processes of the thoracic vertebrae", "Nuchal ligament", "Superior nuchal line", "External occipital protuberance", "Supraspinous ligament"],
    answer: "Transverse processes of the thoracic vertebrae"
  },
  {
    question: "Which blood vessel provides structure number 5?",
    options: ["a. basilica", "a. brachialis", "a. mediana", "a. profunda brachii", "a. axillary", "a. radialis"],
    answer: "a. brachialis"
  },
  {
    question: "Name structure 6",
    options: ['M. serratus anterior', 'M. pectoralis major', 'M. pectoralis minor', 'M. intercostalis externi', 'M. transversus thoracis', 'M. coracobrachialis'],
    answer: 'M. pectoralis minor'
  },
  {
    question: "What is the correct origin of structure 7?",
    options: ["epicondyle medialis humeri and coronoid process ulnae", "epicondyle medialis humeri and olecranon", "epicondyle lateralis humeri and coronoid process ulnae", "epicondyle lateralis humeri and olecranon", "epicondyle lateralis humeri and posterior border of ulna", "epicondyle lateralis humeri and margo posterior humeri"],
    answer: "epicondyle lateralis humeri and posterior border of ulna"
  },
  {
    question: "What are the functions of structure 8?",
    options: ["retroflexion of the shoulder joint", "anteflexion of the shoulder joint", "extension of the elbow", "flexion of the elbow", "retroflexion of the shoulder joint and extension of the elbow", "anteflexion of the shoulder joint and flexion of the elbow"],
    answer: "extension of the elbow"
  },
  {
    question: "What is the insertion of structure 9",
    options: ["styloid process of the ulnae", "styloid process of the radius", "caput ulnae", "scaphoid bone", "metacarpal 1", "os trapezium"],
    answer: "styloid process of the radius"
  },
  {
    question: "Which nerve innervates structure 10?",
    options: ["n radialis ramus profundus", "n radialis ramus superfiscialis", "n ulnaris", "n medianus", "n musculocutaneous", "n antebrachialis"],
    answer: "n medianus"
  },

// Add more questions here...
];

const questionElement = document.getElementById("question");
const optionsElement = document.getElementById("options");

let currentQuestion = 0;
let score = 0;

function showQuestion() {
  const question = quizData[currentQuestion];
  questionElement.innerText = question.question;

  optionsElement.innerHTML = "";
  question.options.forEach(option => {
    const button = document.createElement("button");
    button.innerText = option;
    optionsElement.appendChild(button);
    button.addEventListener("click", selectAnswer);
  });
}

function selectAnswer(e) {
  const selectedButton = e.target;
  const answer = quizData[currentQuestion].answer;

  if (selectedButton.innerText === answer) {
    score++;
  }

  currentQuestion++;

  if (currentQuestion < quizData.length) {
    showQuestion();
  } else {
    showResult();
  }
}

function showResult() {
  questionElement.innerHTML = ""; // Clear question element

  let resultHTML = "<h1>Completed!</h1>";
  resultHTML += `<p>Your score: ${score}/${quizData.length}</p>`;
  resultHTML += "<h2>Lets review the Correct Answers:</h2>";
  

//  quizData.forEach((question, index) => {
//    resultHTML += `<p>${index + 1}. ${question.question} <br>${question.answer}</p>`;

quizData.forEach((question, index) => {
    resultHTML += `<p>${index + 1}. ${question.answer}</p>`;

  });

  // Add a button to retake the quiz
  resultHTML += '<button onclick="retakeQuiz()">Retake Quiz</button>';

  optionsElement.innerHTML = resultHTML;
}

function retakeQuiz() {
  currentQuestion = 0;
  score = 0;
  showQuestion();
}

showQuestion();
