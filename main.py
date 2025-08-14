from app import app
import routes  # ensure routes are registered

# This will be used by Vercel's serverless function
def handler(request, response):
    return app(request.environ, response.start_response)

# For local testing
if __name__ == "__main__":
    app.run(debug=True)

