import React from 'react';
import { Link } from 'react-router-dom';
import { Play, Settings } from 'lucide-react';

const Home: React.FC = () => {
  return (
    <div className="overflow-auto">
      {/* Spacious Hero */}
      <section className="bg-brand-cream">
        <div className="mx-auto max-w-6xl px-6 py-20 text-center">
          <img src="/logo-catherine-ai-partner.png" alt="Catherine AI Partner" className="mx-auto w-80 h-auto object-contain mb-8" />
          <h1 className="text-5xl font-extrabold tracking-tight">Catherine — AI Study Partner</h1>
          <p className="mt-5 text-lg max-w-2xl mx-auto">
            Real-time capture. Instant OCR and Speech-to-Text. Semantic search and contextual Q&A — all in one focused study flow.
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link to="/dashboard" className="btn-primary btn-lg px-8">
              <Play className="h-5 w-5 mr-2" /> Start your study partner
            </Link>
            <Link to="/settings" className="btn-outline btn-lg px-8">
              <Settings className="h-5 w-5 mr-2" /> Settings
            </Link>
          </div>
        </div>
      </section>

      {/* What is Catherine */}
      <section className="bg-brand-sand">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <h2 className="text-3xl font-bold text-center">What is Catherine?</h2>
          <p className="mt-4 text-center max-w-3xl mx-auto">
            Catherine helps you study smarter by capturing your learning context and answering questions with citations. Choose Gemini, OpenAI, or DeepSeek — the pipeline stays the same.
          </p>
          <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card p-6 text-center">
              <h3 className="font-semibold">Real‑time Capture</h3>
              <p className="mt-2 text-sm">Grab screen frames and audio segments continuously with adjustable FPS and sample rate.</p>
            </div>
            <div className="card p-6 text-center">
              <h3 className="font-semibold">OCR + Speech</h3>
              <p className="mt-2 text-sm">Extract text from slides and generate transcripts, then index for instant retrieval.</p>
            </div>
            <div className="card p-6 text-center">
              <h3 className="font-semibold">Contextual Q&A</h3>
              <p className="mt-2 text-sm">Ask questions anytime — Catherine cites relevant snippets from your current session.</p>
            </div>
          </div>
        </div>
      </section>

      {/* About George */}
      <section className="bg-brand-cream">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <h2 className="text-3xl font-bold text-center">Created by George Emil</h2>
          <p className="mt-4 text-center max-w-3xl mx-auto">
            Senior Computer Engineering student focusing on AI, Data Science, embedded systems, and automotive AI. Seeking an AI internship to drive real‑world impact.
          </p>
          <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card p-6">
              <h3 className="font-semibold">Experience</h3>
              <ul className="mt-2 text-sm list-disc pl-5 space-y-1">
                <li>Software Internship at MCV (On‑Site), Jul–Aug 2025</li>
                <li>Data Analysis at NTI, Jul–Sep 2024</li>
                <li>Entrepreneurship at ITIDA, Oct 2023</li>
              </ul>
            </div>
            <div className="card p-6">
              <h3 className="font-semibold">Skills</h3>
              <p className="mt-2 text-sm">Python, C/C++, Embedded C, ML/DL, NLP, CV, TensorFlow, PyTorch, scikit‑learn, OpenCV, Docker, Linux.</p>
              <p className="mt-3 text-sm font-medium">Award: 2nd place worldwide — Shell Eco‑marathon APC (2025).</p>
            </div>
            <div className="card p-6">
              <h3 className="font-semibold">Portfolio</h3>
              <a href="https://georgeemil787.github.io/George-Emil-protfolio/" target="_blank" rel="noreferrer" className="mt-2 inline-block btn-primary">View portfolio</a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;


