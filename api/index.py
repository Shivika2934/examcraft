from app import app
import routes  # ensure all routes load

# Vercel will call this function
def handler(request, response):
    return app(request.environ, response.start_response)

# For local dev
if __name__ == "__main__":
    app.run(debug=True)
