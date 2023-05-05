from barLi_app.app_var import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
