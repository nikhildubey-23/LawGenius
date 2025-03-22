# LawGenius

LawGenius is a Django-based AI-powered legal assistant designed to assist lawyers, law students, common people, judiciary members, and startups with legal queries and document analysis. The system leverages AI to provide insights into offensive security techniques, case predictions, and legal research.

## Features
- **For Lawyers**:
  - Fast research on laws and case decisions.
  - AI-powered case prediction based on past cases.
  - Document analysis for contracts and agreements.

- **For Law Students**:
  - Explanation of case laws, IPC, and CRPC.
  - AI-assisted mock court preparation.
  - Quick resolution of legal queries.

- **For Common People**:
  - Legal information in Hindi for better understanding.
  - Free legal guidance for minor cases.
  - Details on government schemes, RTI, and FIR processes.

- **For Judiciary**:
  - Analysis of old cases for trends and insights.
  - AI-assisted faster trials for small cases.

- **For Companies and Startups**:
  - Legal due diligence for documents.
  - Risk analysis and error detection in contracts.

## Tech Stack
- **Backend**: Django
- **Database**: SQLite3 (stored in `/tmp` on Vercel for temporary storage)
- **AI Model**: `deepseek-r1-distill-llama-70b` via `ChatGroq`
- **Environment Variables**: Managed via `dotenv`

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/lawgenius.git
   cd lawgenius
   ```
2. Create a virtual environment and install dependencies:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up environment variables in a `.env` file:
   ```sh
   GROQ_API_KEY=your_groq_api_key
   ```
4. Run the Django development server:
   ```sh
   python manage.py runserver
   ```

## Usage
- Access the homepage to enter legal queries.
- View past queries and AI-generated responses.
- Clear history when needed.

## API Endpoints
- `POST /` - Submit a legal query.
- `GET /history` - View previous queries and responses.
- `POST /clear_history` - Clear all stored queries.
- `GET /about` - Information about the platform.
- `GET /reachout` - Contact page.

## Deployment
The application is optimized for deployment on **Vercel** with a temporary SQLite database stored in `/tmp`. Ensure necessary environment variables are set before deploying.



