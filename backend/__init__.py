from app import create_app

app = create_app()
# auth api statreted
if __name__ == "__main__":
    app.run(debug=True)