import io
from flask import Flask, request, render_template, redirect, send_file

from pipeline import *

app = Flask(__name__)


@app.route("/")
def index():
    delete_folder("primary_data_pipeline_results")
    if os.path.exists("results.zip"):
        os.remove("results.zip")
    return render_template("index.html")


@app.route("/", methods=['POST'])
def correct_to_pipeline():
    dtypes = None
    parse_dates = None
    if request.method == 'POST':
        dtypes = {}
        parse_dates = []
        for elt in request.form:
            val = request.form.get(elt)
            if val == 'datetime64':
                parse_dates.append(elt)
            elif elt == 'path' or elt == 'sep':
                continue
            else:
                dtypes[elt] = val
    
    csv_params = {
        'filepath_or_buffer': request.form.get('path'),
        'sep': request.form.get('sep'),
        'dtype': dtypes,
        'parse_dates': parse_dates
        }
    params_path = os.path.join(os.path.dirname(request.form.get('path')), "csv_params.json")
    with open(params_path, "w") as json_file:
        json.dump(csv_params, json_file)

    zipfile_name = primary_data_pipeline(params_path)
    response = send_file(f"{zipfile_name}.zip", as_attachment=True)

    # os.remove(f"{zipfile_name}.zip")
    # delete_folder(os.path.dirname(request.form.get('path')))

    return response


@app.route('/columns', methods=['POST'])
def upload_to_correct():

    columns = ""

    if request.method == "POST":

        sep = request.form.get('csv_sep')
        
        dirname = create_result_dir()

        if 'file' in request.files and 'csv_path' not in request.form:
            filename = request.files['file'].filename
            file_content = request.files.get('file').read().decode("utf-8")
            df = pd.read_csv(io.StringIO(file_content), sep=sep)
            df.to_csv(os.path.join(dirname, filename), sep=sep, index=False)

        elif 'csv_path' in request.form and 'file' not in request.files:
            filename = request.form.get('csv_path')
            df = pd.read_csv(filename, sep=sep)
            df.to_csv(os.path.join(dirname, os.path.basename(filename)), sep=sep, index=False)
        else:
            df = None
            filename = ""
            delete_folder(dirname)
        
        columns = form_columns(df)
        csv_params = {
            'path': os.path.join(dirname, filename),
            'sep': sep
            }
        
    return render_template("columns.html", columns=columns, params=csv_params)
    

@app.route("/cancel")
def delete_on_going():
    delete_folder("primary_data_pipeline_results")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
