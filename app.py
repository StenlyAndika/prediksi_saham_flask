from flask import Flask, render_template, request, jsonify
import pymysql
import pandas as pd

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'prediksi_saham'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

db = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)

# Enable Flask Debug Mode
app.config['DEBUG'] = True

class DatabaseConnection:
    def __enter__(self):
        self.connection = db.cursor()
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

@app.route("/")
def home():
    data = {
        'header': 'dashboard'
    }
    print("oke")
    return render_template('dashboard.html', header_data=data)

@app.route("/dataset")
def dataset():  
    try:
        with DatabaseConnection() as cursor:
            cursor.execute("SELECT * FROM dataset")
            res = cursor.fetchall()

        data = {
            'header': 'dataset',
            'result' : res
        }
    
        return render_template('dataset.html', header_data=data)
    except db.Error as e:
        db.rollback()            
        error_message = "An error occurred: " + str(e)
        response = jsonify({'status': 'error', 'message': error_message})
        return response      

@app.route('/add_data', methods=['POST'])
def add_data():
    if request.method == 'POST':        
        open_price = request.form['open']        
        high_price = request.form['open']        
        low_price = request.form['open']        
        close_price = request.form['open']        

        try:
            with DatabaseConnection() as cursor:
                insert_query = "INSERT INTO dataset (open,high,low,close) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_query, (open_price,high_price,low_price,close_price))
            
            db.commit()                        
                    
            response = jsonify({'status': 'success', 'message': 'Data added successfully'})
            return response

        except db.Error as e:
            
            db.rollback()            
            error_message = "An error occurred: " + str(e)
            response = jsonify({'status': 'error', 'message': error_message})
            return response

@app.route('/import_data', methods=['POST'])
def import_data():
    if request.method == 'POST':
        try:
            # Get the uploaded CSV file
            uploaded_file = request.files['file']

            if uploaded_file.filename != '':
                # Read the CSV file using pandas
                df = pd.read_csv(uploaded_file)                

                # Insert data into the "dataset" table
                with DatabaseConnection() as cursor:
                    for index, row in df.iterrows():
                        open_price = row['Open']
                        high_price = row['High']
                        low_price = row['Low']
                        close_price = row['Close']

                        insert_query = "INSERT INTO dataset (open, high, low, close) VALUES (%s, %s, %s, %s)"
                        cursor.execute(insert_query, (open_price, high_price, low_price, close_price))

                # Commit the transaction
                db.commit()

            # Redirect to the same page after importing
            response = jsonify({'status': 'success', 'message': 'Data added successfully'})
            return response

        except pymysql.Error as e:
            # Handle any database errors
            db.rollback()            
            error_message = "An error occurred: " + str(e)
            response = jsonify({'status': 'error', 'message': error_message})
            return response

@app.route("/training")
def training():
    try:
        with DatabaseConnection() as cursor:
            cursor.execute("SELECT * FROM dataset")
            res = cursor.fetchall()

        data = {
            'header': 'training',
            'result' : res
        }
    
        return render_template('training.html', header_data=data)
    except db.Error as e:
        db.rollback()            
        error_message = "An error occurred: " + str(e)
        response = jsonify({'status': 'error', 'message': error_message})
        return response 

@app.route("/testing")
def testing():
    data = {
        'header': 'testing'
    }
    return render_template('testing.html', header_data=data)

@app.route("/prediksi")
def prediksi():
    data = {
        'header': 'prediksi'
    }
    return render_template('prediksi.html', header_data=data)

@app.route("/log-activity")
def log():
    data = {
        'header': 'log'
    }
    return render_template('log.html', header_data=data)


if __name__ == '__main__':
    app.run(debug=True)