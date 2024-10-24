const quizData = [
  {
    question: "Name structure number 1",
    options: ["m quadratus lumborum", "m iliacus", "m psoas major", "m psoas minor", "m multifidus", "m transversus abdominis"],
    answer: "m iliacus"
  },
  {
    question: "Name structure number 2",
    options: ["m vastus lateralis", "m vastus intermedius", "m tractus iliotibialis", "m tensor facia latae", "m vastus medialis", "m rectus femoris"],
    answer: "m tensor facia latae"
  },
  {
    question: "Name structure number 3",
    options: ["n peroneus communis", "n obturatorius", "n ischiadicus", "n femoralis", "n tibialis", "n fibularis"],
    answer: "n femoralis"
  },
  {
    question: "Which of the following statements is correct for structure 4?",
    options: ["this nerve innervates the m adductor longus", "this artery supplies blood to the tensor fascia latae", "this artery supplies blood to the vastus lateralis", "this vein receives blood from the v saphena magna", "this vein goes to the external iliac crest", "this artery is located in the lacuna vasorum"],
    answer: "this artery is located in the lacuna vasorum"
  },

  {
    question: "Which statement is false for structure 5?",
    options: ["the origin of this muscle is the anterior superior iliac spine", "the insertion of this muscle is the facies medialis of the tibia, medial to the tuberosity", "the innervation of this muscle is the n femoralis", "the blood supply of this muscle is the a circumflexa femoris medialis", "this muscle does, among other things, flexion and abduction of the thigh", "this muscle is part of the pes anserinus"],
    answer: "the blood supply of this muscle is the a circumflexa femoris medialis"
  },

  {
    question: "Name structure number 6",
    options: ["m adductor longus", "m adductor brevis", "m adductor magnus", "m adductor minimus", "m pectineus", "m gracilis"],
    answer: "m adductor longus"
  },

  {
    question: "Name structure number 7",
    options: ["a tibialis anterior", "a tibialis posterior", "n peroneus superfiscialis", "n peroneus profundus", "v saphenous parva", "v saphena magna"],
    answer: "v saphena magna"
  },

  {
    question: "What structure is not in this compartment (number 8)?",
    options: ["a tibialis posterior", "a peronea", "n tibialis", "m plantaris", "m tibialis posterior", "m flexor hallucis longus"],
    answer: "m plantaris"
  },

  {
    question: "What is the origin of structure 9?",
    options: ["L4-S3", "L5-S2", "L1-L4", "T12-L5", "S1-S3", "S1-Co2"],
    answer: "L4-S3"
  },

  {
    question: "What is the insertion of structure 10?",
    options: ["fossa intertrochanterica femoris", "linea intertrochanterica femoris", "greater trochanter femoris", "lesser trochanter femoris", "linea aspera labium mediale", "linea aspera labium laterale"],
    answer: "greater trochanter femoris"
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
