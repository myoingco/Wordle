# create wordle game
import random
from typing import List
from flask import Flask, request, jsonify
app = Flask(__name__)
WORD_LIST = [
    "apple", "berry", "mango", "peach", "grape", "lemon", "table", "chair", "plant", "brick",
    "crane", "flame", "glove", "horse", "jelly", "knife", "liver", "mouse", "nurse", "ocean",
    "piano", "queen", "river", "sheep", "tiger", "uncle", "vivid", "whale", "xenon", "yacht",
    "zebra", "angel", "blaze", "crown", "daisy", "eagle", "frost", "giant", "honey", "ivory",
    "joker", "karma", "latch", "mirth", "noble", "orbit", "pride", "quest", "rider", "sugar"
]  # 50 five-letter words
MAX_ATTEMPTS = 6
class WordleGame:
    def __init__(self):
        self.secret_word = random.choice(WORD_LIST)
        self.attempts = 0
        self.max_attempts = MAX_ATTEMPTS
        self.game_over = False

    def guess(self, word: str) -> dict:
        if self.game_over:
            return {"feedback": ["Game over! The secret word was: " + self.secret_word], "colors": ["black"]*5}

        if len(word) != 5:
            return {"feedback": ["Invalid guess length. Please enter a 5-letter word."], "colors": ["black"]*5}

        self.attempts += 1

        feedback = []
        colors = []
        for i in range(len(word)):
            feedback.append(word[i])
            if word[i] == self.secret_word[i]:
                colors.append("green")
            elif word[i] in self.secret_word:
                colors.append("gold")
            else:
                colors.append("red")

        if word == self.secret_word:
            self.game_over = True
            return {"feedback": ["Congratulations! You've guessed the word!"], "colors": ["green"]*5}

        if self.attempts >= self.max_attempts:
            self.game_over = True
            return {"feedback": ["Game over! The secret word was: " + self.secret_word], "colors": ["black"]*5}

        return {"feedback": feedback, "colors": colors}
games = {}
@app.route('/')
def home():
    return '''
    <h1>Welcome to Mei's Wordle App!</h1>
    <button onclick="startGame()">Start Game</button>
    <button onclick="getHint()">Hint</button>
    <button onclick="newWord()">New Word</button>
    <div id="output" style="margin-top:20px;"></div>
    <script>
    let gameId = null;
    function startGame() {
        fetch('/start', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                gameId = data.game_id;
                document.getElementById('output').innerHTML = 'Game started! Game ID: ' + gameId + '<br>Enter your guess: <input id="guessInput" type="text" maxlength="5"> <button onclick="submitGuess()">Submit</button>';
            });
    }
    function submitGuess() {
        const guess = document.getElementById('guessInput').value;
        fetch('/guess', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({game_id: gameId, word: guess})
        })
        .then(response => response.json())
        .then(data => {
            let feedback = data.feedback;
            let colors = data.colors;
            let html = 'Feedback: [';
            for (let i = 0; i < feedback.length; i++) {
                let letter = feedback[i];
                let color = colors[i];
                html += '<span style="color:' + color + ';font-weight:bold">"' + letter + '"</span>';
                if (i < feedback.length - 1) html += ',';
            }
            html += ']';
            document.getElementById('output').innerHTML += '<br>' + html;
        });
    }
    function getHint() {
        if (!gameId) {
            document.getElementById('output').innerHTML += '<br>Please start a game first!';
            return;
        }
        fetch('/hint', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({game_id: gameId})
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('output').innerHTML += '<br>Hint: ' + data.hint;
        });
    }
    function newWord() {
        fetch('/newword', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                gameId = data.game_id;
                document.getElementById('output').innerHTML = 'New game started! Game ID: ' + gameId + '<br>Enter your guess: <input id="guessInput" type="text" maxlength="5"> <button onclick="submitGuess()">Submit</button>';
            });
    }
    </script>
    '''
@app.route('/start', methods=['POST'])
def start_game():
    game_id = str(len(games) + 1)
    games[game_id] = WordleGame()
    return jsonify({"game_id": game_id})
@app.route('/guess', methods=['POST'])
def make_guess():
    data = request.json
    game_id = data.get("game_id")
    word = data.get("word")

    if game_id not in games:
        return jsonify({"error": "Invalid game ID."}), 400

    game = games[game_id]
    result = game.guess(word)
    return jsonify(result)
if __name__ == '__main__':
    app.run(debug=True)
