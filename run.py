from app import create_app   # importing factory functioun or our instance


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)