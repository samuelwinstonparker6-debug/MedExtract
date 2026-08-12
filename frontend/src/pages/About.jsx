import React from 'react';
import { Users, ClipboardList, Sparkles } from 'lucide-react';

const contributors = [
  {
    name: 'Prajwal Sam',
    responsibility: 'Project coordination, backend API design, and feature integration',
  },
  {
    name: 'Yeshaswini K',
    responsibility: 'Frontend implementation, UI layout, and client-side routing',
  },
  {
    name: 'Ravi Chaitanya',
    responsibility: 'OCR data extraction, document processing logic, and heuristics',
  },
  {
    name: 'Roshan Joel',
    responsibility: 'Testing, validation, deployment preparation, and documentation',
  },
];

export default function About() {
  return (
    <div className="flex flex-col gap-8 h-full">
      <div className="relative overflow-hidden bg-surface border border-gray-700 rounded-2xl p-8">
        <div className="absolute -top-10 -right-10 w-64 h-64 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-10 -left-10 w-48 h-48 bg-blue-400/5 rounded-full blur-2xl pointer-events-none" />
        <div className="relative flex items-center gap-5">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-sky-500 to-blue-500 flex items-center justify-center shadow-lg shadow-sky-500/25 flex-shrink-0">
            <Users className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-black tracking-tight mb-1">About This Project</h1>
            <p className="text-gray-400 text-sm leading-relaxed max-w-xl">
              This application was built by a team working across backend, frontend, OCR,
              and QA. The About page documents the contributors and their split duties.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="bg-surface border border-gray-700 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-5 h-5 text-sky-400" />
            <h2 className="text-lg font-bold">Project Overview</h2>
          </div>
          <div className="space-y-3 text-gray-300 leading-relaxed">
            <p>
              MedExtract is a document extraction and verification platform tailored for medical billing documents.
              It converts scanned bills into structured data using OCR, then validates that data against trusted templates.
            </p>
            <p>
              The system also supports secure license key generation and verification so patient identifiers
              can be matched with authorized document records during upload and review.
            </p>
            <p>
              This project combines backend processing, frontend usability, and audit-ready controls to make
              medical document validation faster, more accurate, and easier to manage.
            </p>
            <p>
              The solution is designed for real-world use with authenticated APIs, clear workflow navigation,
              and a modular architecture that can be extended to additional document types.
            </p>
          </div>
        </div>

        <div className="bg-surface border border-gray-700 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            <ClipboardList className="w-5 h-5 text-sky-400" />
            <h2 className="text-lg font-bold">Responsibilities</h2>
          </div>
          <div className="space-y-3">
            {contributors.map((contributor) => (
              <div key={contributor.name} className="rounded-2xl border border-gray-800 bg-background/70 p-4">
                <p className="text-sm text-gray-400 uppercase tracking-widest mb-2">{contributor.name}</p>
                <p className="text-sm text-gray-200">{contributor.responsibility}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-surface border border-gray-700 rounded-2xl p-6">
        <h2 className="text-lg font-bold mb-3">How to update this page</h2>
        <p className="text-gray-400 text-sm leading-relaxed">
          Replace the placeholder names and responsibilities with the actual team members
          and their duties once they are finalized. This page is designed to document
          the split of work clearly.
        </p>
      </div>
    </div>
  );
}
