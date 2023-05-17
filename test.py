from flask import Flask, jsonify

# define Flask instance
app = Flask(__name__)

# Define URL
@app.route('/books')
# Map function to URL and define dictionary
def return_json():
   my_dict = {"Mystery": ["The Hound of the Baskervilles",
                          "And Then There Were None"],
              "Science Fiction": ["A Canticle for Leibowitz",
                                  "That Hideous Strength",
                                  "Speaker for the Dead"],
              "Fantasy": ["The Way of Kings", "Mistborn"],
              "Biography": "Open"}

   return jsonify(my_dict)

if __name__ == '__main__':
   app.run()