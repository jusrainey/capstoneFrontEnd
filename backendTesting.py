from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app) 

toggle = True

distinct_coords_1 = {
    'board1': {'lat': 33.423497319542484, 'lng': -111.93980010024928},
    'board2': {'lat': 33.423497319542484, 'lng': -111.93932453429524}
}

distinct_coords_2 = {
    'board1': {'lat': 33.423497319542484, 'lng': -111.93980010024928},
    'board2': {'lat': 33.423497319542484, 'lng': -111.93941453429524}
}

@app.route('/api/coordinates', methods=['GET'])
def get_coordinates():
    """
    Dummy API endpoint to test updation of board position
    """
    global toggle
    selected = distinct_coords_1 if toggle else distinct_coords_2
    now_iso = datetime.utcnow().isoformat() + 'Z'

    response = {
        'board1': {
            'lat': selected['board1']['lat'],
            'lng': selected['board1']['lng'],
            'last_signal': now_iso
        },
        'board2': {
            'lat': selected['board2']['lat'],
            'lng': selected['board2']['lng'],
            'last_signal': now_iso
        }
    }

    #toggle functionality to test movement
    toggle = not toggle
    return jsonify(response)

if __name__ == '__main__':

    app.run(host='127.0.0.1', port=8000, debug=True)
