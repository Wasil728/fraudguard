# -*- coding: utf-8 -*-
"""
Generates the comprehensive Hinglish presentation guide HTML and compiles it to PDF via headless Edge.
"""
import os
import subprocess

html_content = """<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<title>FraudGuard - 14-Slide Complete Hinglish Presentation Guide</title>
<style>
    @page {
        size: A4;
        margin: 14mm 14mm 16mm 14mm;
        @bottom-right {
            content: "Page " counter(page);
            font-size: 8pt;
            color: #64748b;
        }
    }
    body {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        background: #ffffff;
        line-height: 1.5;
        font-size: 9.5pt;
        margin: 0;
        padding: 0;
    }
    .header-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: #ffffff;
        padding: 18px 20px;
        border-radius: 8px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .header-banner .college {
        font-size: 9.5pt;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #93c5fd;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .header-banner h1 {
        font-size: 19pt;
        margin: 0 0 6px 0;
        color: #ffffff;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .header-banner .subtitle {
        font-size: 11pt;
        color: #cbd5e1;
        margin-bottom: 12px;
    }
    .meta-grid {
        display: grid;
        grid-template-columns: 1.2fr 1fr;
        gap: 12px;
        background: rgba(255, 255, 255, 0.08);
        padding: 10px 14px;
        border-radius: 6px;
        font-size: 8.5pt;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .meta-grid strong {
        color: #67e8f9;
    }

    .toc-table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0 20px 0;
        font-size: 8.5pt;
    }
    .toc-table th {
        background: #f1f5f9;
        color: #0f172a;
        font-weight: 700;
        text-align: left;
        padding: 6px 10px;
        border: 1px solid #cbd5e1;
    }
    .toc-table td {
        padding: 5px 10px;
        border: 1px solid #e2e8f0;
    }
    .toc-table tr:nth-child(even) td {
        background: #f8fafc;
    }

    .slide-card {
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        margin-bottom: 16px;
        background: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        page-break-inside: avoid;
        overflow: hidden;
    }
    .slide-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f8fafc;
        padding: 8px 14px;
        border-bottom: 1px solid #e2e8f0;
    }
    .slide-title {
        font-size: 11.5pt;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
    }
    .speaker-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 8pt;
        font-weight: 700;
        letter-spacing: 0.3px;
    }
    .speaker-wasil { background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }
    .speaker-sufiyan { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .speaker-tayyab { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .speaker-hasan { background: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }

    .slide-body {
        padding: 12px 14px;
    }

    .section-block {
        margin-bottom: 10px;
    }
    .section-block:last-child {
        margin-bottom: 0;
    }
    .section-label {
        font-size: 9pt;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .label-concept { color: #0284c7; }
    .label-speech { color: #15803d; }
    .label-viva { color: #b45309; }

    .concept-box {
        background: #f0f9ff;
        border-left: 4px solid #0284c7;
        padding: 8px 12px;
        border-radius: 0 4px 4px 0;
        font-size: 9pt;
        color: #0c4a6e;
    }
    .speech-box {
        background: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 9px 12px;
        border-radius: 0 4px 4px 0;
        font-size: 9.3pt;
        color: #14532d;
        font-style: normal;
    }
    .speech-box p {
        margin: 0 0 6px 0;
    }
    .speech-box p:last-child {
        margin: 0;
    }
    .speech-box ul {
        margin: 4px 0;
        padding-left: 18px;
    }
    .viva-box {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 8px 12px;
        border-radius: 0 4px 4px 0;
        font-size: 8.8pt;
        color: #78350f;
    }
    .viva-q {
        font-weight: 700;
        color: #9a3412;
    }
    .viva-a {
        color: #1e293b;
        margin-top: 3px;
    }

    .code-badge {
        font-family: 'Consolas', monospace;
        background: #e2e8f0;
        padding: 1px 5px;
        border-radius: 3px;
        font-size: 8.5pt;
        color: #0f172a;
    }

    .golden-rules {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 14px 18px;
        margin-top: 20px;
        page-break-inside: avoid;
    }
    .golden-rules h3 {
        margin: 0 0 8px 0;
        color: #92400e;
        font-size: 12pt;
    }
    .golden-rules ol {
        margin: 0;
        padding-left: 20px;
        font-size: 9.2pt;
        color: #78350f;
    }
    .golden-rules li {
        margin-bottom: 6px;
    }

    .page-break {
        page-break-before: always;
    }
</style>
</head>
<body>

<!-- Header Banner -->
<div class="header-banner">
    <div class="college">Sagar Institute of Science & Technology (SISTec), Bhopal &bull; Department of CSE (AI & DS)</div>
    <h1>FraudGuard &bull; Slide-by-Slide Hinglish Presentation Guide</h1>
    <div class="subtitle">Complete Presentation Script, Conceptual Clarity & Winning Defense Answers for Evaluators</div>
    
    <div class="meta-grid">
        <div>
            <strong>Project Title:</strong> FraudGuard: Real-Time UPI Fraud Detection & Explainable AI<br>
            <strong>Under the Guidance of:</strong> Prof. Sajid Khan Sir (Project Guide) &bull; Prof. Ruchi Jain Ma'am (Coordinator)
        </div>
        <div>
            <strong>Team Members:</strong><br>
            &bull; Wasil Ali (0187AS241150) &bull; Mohammad Tayyab (0187AS241077)<br>
            &bull; Mohammad Hasan Rizvi (0187AS241082) &bull; Sufiyan Beg (0187AS241031)
        </div>
    </div>
</div>

<!-- Presentation Roster -->
<table class="toc-table">
    <thead>
        <tr>
            <th style="width: 8%;">Slide</th>
            <th style="width: 42%;">Slide Title & Topic</th>
            <th style="width: 25%;">Speaker</th>
            <th style="width: 25%;">Core Focus</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Slide 1</strong></td>
            <td>Title Slide: Project Introduction & Team Accreditation</td>
            <td><span class="speaker-tag speaker-wasil">Wasil Ali</span></td>
            <td>Greeting, Project Name, Scope</td>
        </tr>
        <tr>
            <td><strong>Slide 2</strong></td>
            <td>The UPI Fraud Epidemic (Problem Statement)</td>
            <td><span class="speaker-tag speaker-wasil">Wasil Ali</span></td>
            <td>24B txns, Account Takeover, Static Rules Fail</td>
        </tr>
        <tr>
            <td><strong>Slide 3</strong></td>
            <td>Origin of the Idea & Proposed 5-Layer Solution</td>
            <td><span class="speaker-tag speaker-wasil">Wasil Ali</span></td>
            <td>Behavior vs Amount, 5-layer pipeline</td>
        </tr>
        <tr>
            <td><strong>Slide 4</strong></td>
            <td>FraudGuard vs Existing Systems (Comparison)</td>
            <td><span class="speaker-tag speaker-wasil">Wasil Ali</span></td>
            <td>Table comparison, 1.8ms speed, XAI edge</td>
        </tr>
        <tr>
            <td><strong>Slide 5</strong></td>
            <td>Functional & Non-Functional Requirements</td>
            <td><span class="speaker-tag speaker-sufiyan">Sufiyan Beg</span></td>
            <td>System duties, 1.8ms latency, DPDP compliance</td>
        </tr>
        <tr>
            <td><strong>Slide 6</strong></td>
            <td>Use Case Diagram (System Interactions)</td>
            <td><span class="speaker-tag speaker-sufiyan">Sufiyan Beg</span></td>
            <td>UPI User vs Bank Analyst, &laquo;include&raquo; flow</td>
        </tr>
        <tr>
            <td><strong>Slide 7</strong></td>
            <td>Navigation & User Flow Diagram</td>
            <td><span class="speaker-tag speaker-sufiyan">Sufiyan Beg</span></td>
            <td>Decision tree, Red/Green dial triggers</td>
        </tr>
        <tr>
            <td><strong>Slide 8</strong></td>
            <td>Dataset & Data Privacy (DPDP Act, 2023)</td>
            <td><span class="speaker-tag speaker-tayyab">Mohammad Tayyab</span></td>
            <td>PaySim 6.36M rows, 0.13% class imbalance, DPDP Act</td>
        </tr>
        <tr>
            <td><strong>Slide 9</strong></td>
            <td>Smart Features: Tracking the Money Path (2 Clues)</td>
            <td><span class="speaker-tag speaker-tayyab">Mohammad Tayyab</span></td>
            <td>errorBalanceOrig & errorBalanceDest equations</td>
        </tr>
        <tr>
            <td><strong>Slide 10</strong></td>
            <td>ML Model Pipeline Diagram (Offline vs Online)</td>
            <td><span class="speaker-tag speaker-hasan">Mohammad Hasan Rizvi</span></td>
            <td>Phase 1 Training vs Phase 2 1.8ms Live Inference</td>
        </tr>
        <tr>
            <td><strong>Slide 11</strong></td>
            <td>Why We Chose XGBoost over Others</td>
            <td><span class="speaker-tag speaker-hasan">Mohammad Hasan Rizvi</span></td>
            <td>Rejecting Logistic Reg & Deep Learning, tabular edge</td>
        </tr>
        <tr>
            <td><strong>Slide 12</strong></td>
            <td>Explainable AI: No Hidden Secrets (TreeSHAP)</td>
            <td><span class="speaker-tag speaker-hasan">Mohammad Hasan Rizvi</span></td>
            <td>RBI mandate, Red risk factors vs Green safety signals</td>
        </tr>
        <tr>
            <td><strong>Slide 13</strong></td>
            <td>Live Simulator: Testing the System</td>
            <td><span class="speaker-tag speaker-hasan">Mohammad Hasan Rizvi</span></td>
            <td>4 Presets, live demo workflow, audit logging</td>
        </tr>
        <tr>
            <td><strong>Slide 14</strong></td>
            <td>Research, References & Concluding Remarks</td>
            <td><span class="speaker-tag speaker-wasil">Wasil Ali</span></td>
            <td>Academic citations, Future Scope, Q&A invite</td>
        </tr>
    </tbody>
</table>

<!-- ========================================== -->
<!-- SLIDE 1 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 1: Title Slide (Introduction & Team Accreditation)</div>
        <span class="speaker-tag speaker-wasil">Speaker: Wasil Ali</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                Yeh introductory slide hai. Evaluators (Sajid Khan Sir aur Ruchi Jain Ma'am) ko warm greeting deni hai, project ka title bold aur clear bolna hai, aur apni team ke sabhi members ka role introduce karna hai.
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Good morning Sajid Sir, Ruchi Ma'am, and respected evaluators."</em></p>
                <p><em>"Hum CSE-AIDS department se hain, aur hamara Minor Project-I ka title hai: <strong>FraudGuard: Real-Time UPI Fraud Detection & Explainable AI Architecture</strong>."</em></p>
                <p><em>"Hamari team mein main <strong>Wasil Ali</strong>, mere saath <strong>Mohammad Tayyab</strong>, <strong>Mohammad Hasan Rizvi</strong>, aur <strong>Sufiyan Beg</strong> hain."</em></p>
                <p><em>"Sir, hamara main objective hai high-frequency UPI transactions ko <strong>2 milliseconds ke andar verify karna</strong> aur bank analysts ko ek transparent explanation provide karna ki koi transaction fraud kyun declare ki gayi."</em></p>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Aapke project ki core USP (Unique Selling Proposition) kya hai jo standard fraud systems mein nahi hoti?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Ma'am, standard systems 'Black Box' hote hain jo sirf flag karte hain par reason nahi batate. FraudGuard ki USP <strong>TreeSHAP Explainable AI</strong> hai jo 1.8ms ke andar top mathematically-backed reasons batata hai, jisse RBI compliance maintain rehti hai."</div>
            </div>
        </div>
    </div>
</div>

<!-- ========================================== -->
<!-- SLIDE 2 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 2: The UPI Fraud Epidemic (Problem Statement)</div>
        <span class="speaker-tag speaker-wasil">Speaker: Wasil Ali</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                India mein har mahine 24 billion se zyada UPI payments hote hain. Purane banking rules (jaise: ₹1 Lakh se upar ka transfer roko) fail ho chuke hain kyunki hackers chote-chote chunks mein account khali karte hain (Smurfing attack).
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Sir, jaise hum sab jante hain ki India mein har mahine <strong>24 Billion se zyada UPI transactions</strong> execute ho rahe hain. Lekin jitni speed se payments expand hui hain, financial frauds bhi utni hi tezi se sophisiticated ho gaye hain:"</em></p>
                <ul>
                    <li><em><strong>1. Account Takeover:</strong> Hackers social engineering, phishing ya screen-share apps se victim ka account compromise karte hain aur seconds ke andar account sweep kar dete hain.</em></li>
                    <li><em><strong>2. Static Rules Fail:</strong> Traditional banks fixed threshold lagate hain (jaise: '₹50,000 se bada transfer flag karo'). Fraudsters is limit ko bypass karne ke liye paisa chote-chote tukdon mein split kar dete hain jise banking term mein <strong>Smurfing</strong> kaha jata hai.</em></li>
                    <li><em><strong>3. Mule Account Chains:</strong> Chori ka paisa turant mule accounts ki chain mein route hota hai aur ATM se cash liquidate kar liya jata hai.</em></li>
                </ul>
                <p><em>"Isliye static rules helpless ho chuke hain, aur hume ek aisa dynamic Machine Learning system chahiye jo balance behavior ko millisecond level par scan kare."</em></p>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Agar hacker ₹10,000 nikalta hai, toh aapka system use kaise pakdega agar amount chota hai?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, hamara model transaction ke flat amount par depend nahi karta. Hamara model check karta hai ki ₹10,000 transfer hone ke baad sender ka balance <strong>abruptly ₹0 ho gaya ya nahi</strong>. Pure account ka wipe-out hona hamari engineered balance equation se turant alarm raise karta hai."</div>
            </div>
        </div>
    </div>
</div>

<div class="page-break"></div>

<!-- ========================================== -->
<!-- SLIDE 3 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 3: Origin of the Idea & Proposed 5-Layer Solution</div>
        <span class="speaker-tag speaker-wasil">Speaker: Wasil Ali</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                FraudGuard ka architectural solution 5 layers par bana hai: REST API &rarr; Feature Engineering &rarr; XGBoost Inference &rarr; TreeSHAP Explainability &rarr; Audit & Analyst Workflow.
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Is critical security gap ko solve karne ke liye humne design kiya <strong>FraudGuard</strong>."</em></p>
                <p><em>"Hamara solution ek robust <strong>5-layer operational architecture</strong> follow karta hai:"</em></p>
                <ul>
                    <li><em><strong>Layer 1 (Ingestion API):</strong> Django REST API payment payload ko microsecond latency mein intercept karta hai.</em></li>
                    <li><em><strong>Layer 2 (Mathematical Feature Engineering):</strong> Raw amount ke sath-sath sender aur receiver ke balance discrepancies calculate hoti hain.</em></li>
                    <li><em><strong>Layer 3 (Machine Learning Core):</strong> XGBoost model 0 se 100% ka continuous risk score calculate karta hai.</em></li>
                    <li><em><strong>Layer 4 (Explainable AI Engine):</strong> TreeSHAP har feature ka positive ya negative risk contribution compute karta hai.</em></li>
                    <li><em><strong>Layer 5 (Audit & Review Layer):</strong> MySQL database mein immutable logs save hote hain aur flagged transactions compliance officer ke dashboard par render hoti hain."</em></li>
                </ul>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Aapne architecture mein Django kyun choose kiya, Node.js ya FastAPI kyun nahi?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, Python data science aur ML libraries (XGBoost, SHAP, NumPy) ka native ecosystem hai. Django enterprise-grade ORM, CSRF security aur admin workflows provide karta hai jisse ML inference aur transactional database bina kisi inter-process latency ke directly communicate karte hain."</div>
            </div>
        </div>
    </div>
</div>

<!-- ========================================== -->
<!-- SLIDE 4 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 4: FraudGuard vs Existing Systems (Comparison)</div>
        <span class="speaker-tag speaker-wasil">Speaker: Wasil Ali</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                Table ke points ko clear contrast karna hai: Purane systems = Fixed amount, High False Positives, Zero reason, Slow. FraudGuard = Dynamic ML, 99.57% Recall, Sub-2ms speed, TreeSHAP report card.
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Sir, is slide mein humne traditional banking approaches aur FraudGuard ka direct comparative analysis present kiya hai:"</em></p>
                <ul>
                    <li><em><strong>Detection Mechanism:</strong> Existing systems rigid IF-THEN rules use karte hain, jabki FraudGuard non-linear pattern-learning XGBoost trees use karta hai.</em></li>
                    <li><em><strong>Split Payments (Smurfing):</strong> Existing systems chote payments ko blind-spot bana lete hain, jabki FraudGuard origin balance depletion ko track karke unhe catch karta hai.</em></li>
                    <li><em><strong>Explainability:</strong> Traditional AI binary yes/no deti hai jisse customer support explain nahi kar pata. FraudGuard <strong>TreeSHAP transparency card</strong> generate karta hai.</em></li>
                    <li><em><strong>Latency:</strong> Banking SLA sub-5ms mangta hai, hamara pipeline decision <strong>1.8 milliseconds</strong> mein deliver karta hai."</em></li>
                </ul>
                <p><em>"Ab main invite karta hoon <strong>Sufiyan Beg</strong> ko aage ke system requirements aur engineering diagrams explain karne ke liye."</em></p>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Agar bank ka existing rule-based engine chal raha hai, toh kya FraudGuard use replace karega ya complement?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, FraudGuard hybrid model support karta hai. Initial sanction checks (jaise sanctioned country ya blocked IFSC) standard rule engine karega, aur immediate behavioral inference FraudGuard 1.8ms mein evaluate karega."</div>
            </div>
        </div>
    </div>
</div>

<div class="page-break"></div>

<!-- ========================================== -->
<!-- SLIDE 5 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 5: Functional & Non-Functional Requirements</div>
        <span class="speaker-tag speaker-sufiyan">Speaker: Sufiyan Beg</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                Functional = System kya functionality deta hai (API input, 2 math clues, XGBoost scoring, alert generation, review workflow). Non-Functional = Quality parameters (1.8ms speed, DPDP privacy, zero downtime).
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Thank you Wasil."</em></p>
                <p><em>"Sir, hamare engineering requirements do major categories mein structured hain:"</em></p>
                <ul>
                    <li><em><strong>Functional Requirements:</strong> System 6 transactional inputs accept karta hai (type, amount, sender/receiver balances). Background mein do mathematical discrepancy features calculate karta hai, continuous risk probability output karta hai, aur dynamic risk settings ke base par instant alert banata hai.</em></li>
                    <li><em><strong>Non-Functional Requirements:</strong> Sabse primary metric hai <strong>Inference Latency (1.8 ms)</strong> taaki real-time UPI switch me koi lag na aaye. Second hai <strong>Security & Compliance</strong> jahan India ka DPDP Act follow hota hai, aur third hai <strong>Reliability</strong> with transactional ACID guarantees in MySQL."</em></li>
                </ul>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Aapne 1.8ms latency measure kaise ki? Kya yeh network latency include karti hai?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, 1.8ms hamari pure in-memory ML inference + feature calculation latency hai. Server benchmarking ke waqt humne Python ke high-precision time modules se measure kiya hai, jo banking gateway ke 50ms total timeout budget ke andar aasaani se fit hota hai."</div>
            </div>
        </div>
    </div>
</div>

<!-- ========================================== -->
<!-- SLIDE 6 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 6: Use Case Diagram (System Interactions)</div>
        <span class="speaker-tag speaker-sufiyan">Speaker: Sufiyan Beg</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                Do primary actors hain: UPI User (transaction sender) aur Bank Analyst (investigator). UML mein «include» ka matlab hota hai ki yeh internal processes automatically trigger hote hain.
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Sir, yeh hamara formal <strong>UML Use Case Diagram</strong> hai jisme do distinct primary actors interact karte hain:"</em></p>
                <ul>
                    <li><em><strong>Actor 1: UPI User</strong> — Jo peer-to-peer payment initiate karta hai aur system se instant Approved ya Blocked decision receive karta hai.</em></li>
                    <li><em><strong>Actor 2: Bank Compliance Analyst</strong> — Jo interactive simulator run karta hai, risk dial monitor karta hai, TreeSHAP report inspect karta hai, aur review statuses update karta hai.</em></li>
                    <li><em><strong>Internal Include Relationships:</strong> Diagram mein 'Calculate Balance Clues', 'Score Risk', aur 'Save Audit Log' dashed lines se linked hain, jiska matlab hai ki transaction initiate hote hi yeh teeno internally mandatory execute hote hain."</em></li>
                </ul>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Use Case diagram mein &laquo;include&raquo; aur &laquo;extend&raquo; mein kya fark hota hai yahan?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, &laquo;include&raquo; mandatory hota hai—jaise risk score har transaction ke liye calculate hoga hi hoga. Jabki &laquo;extend&raquo; conditional hota hai—jaise 'Create Fraud Alert' sirf tabhi execute hoga jab risk score threshold se upar cross hoga."</div>
            </div>
        </div>
    </div>
</div>

<div class="page-break"></div>

<!-- ========================================== -->
<!-- SLIDE 7 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 7: Navigation & User Flow Diagram</div>
        <span class="speaker-tag speaker-sufiyan">Speaker: Sufiyan Beg</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                Flowchart ka core: User input &rarr; Feature calculation &rarr; XGBoost score &rarr; Threshold comparison &rarr; Red dial (Block + Alert) vs Green dial (Approve).
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Yeh diagram hamare system ka operational <strong>User Flow & Decision Tree</strong> demonstrate karta hai:"</em></p>
                <ul>
                    <li><em>Pehle user UI ya API par transaction details load karta hai (jaise hamare live presets).</em></li>
                    <li><em>Backend mein immediate validation hoti hai, balance features extract hote hain, aur XGBoost engine probability produce karta hai.</em></li>
                    <li><em><strong>Conditional Branch:</strong> Agar Risk Score configured threshold (e.g. 50%) se greater hai, transaction turant <strong>BLOCK</strong> hoti hai, UI par <strong>Red Dial</strong> trigger hota hai, aur detailed SHAP breakdown render hoti hai.</em></li>
                    <li><em>Agar Risk Score safe zone mein hai, transaction instantly <strong>APPROVE</strong> hoti hai aur <strong>Green Dial</strong> show hota hai. Dono cases MySQL audit ledger mein record hote hain."</em></li>
                </ul>
                <p><em>"Ab main stage hand over karta hoon <strong>Mohammad Tayyab</strong> ko hamara dataset aur mathematical feature engineering explain karne ke liye."</em></p>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Threshold ko hardcode kiya hai ya dynamically change kar sakte hain?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, dynamic hai. Hamare system mein `RiskSetting` model hai jahan analyst bina server restart kiye threshold 1% se 99% ke beech live modify kar sakta hai."</div>
            </div>
        </div>
    </div>
</div>

<!-- ========================================== -->
<!-- SLIDE 8 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 8: Dataset & Data Privacy (DPDP Act, 2023)</div>
        <span class="speaker-tag speaker-tayyab">Speaker: Mohammad Tayyab</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                Teacher ka classic sawal: "Real bank data kyun nahi use kiya?" Jawab: India ka DPDP Act 2023 citizen banking data ko protect karta hai. Isliye international benchmark PaySim use kiya (6.36 Million rows, extreme class imbalance 0.13% fraud).
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Thank you Sufiyan."</em></p>
                <p><em>"Sir, machine learning mein data selection sabse critical step hota hai. Aksar evaluators puchte hain ki humne real bank accounts ka data kyun nahi liya:"</em></p>
                <ul>
                    <li><em><strong>Legal & Ethical Compliance:</strong> India ke <strong>Digital Personal Data Protection (DPDP) Act, 2023</strong> aur RBI cybersecurity guidelines ke tehat kisi bhi customer ka live financial PII data bina explicit statutory license ke use karna strictly prohibited hai.</em></li>
                    <li><em><strong>PaySim Dataset:</strong> Isliye humne <strong>PaySim synthetic financial benchmark</strong> use kiya, jo actual African mobile money service ke aggregated logs par calibrated hai. Isme <strong>6.36 Million (63.6 Lakh)</strong> transactions hain.</em></li>
                    <li><em><strong>Real-World Class Imbalance:</strong> Is dataset mein 99.87% legitimate data hai aur sirf <strong>0.13% fraud</strong> hai. Real life mein bhi har hazaar transactions mein se sirf 1-2 fraud hote hain. Is extreme imbalance ko handle karne ke liye stratified techniques lagayi gayi hain."</em></li>
                </ul>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Class Imbalance kya hota hai aur isse model training par kya asar padta hai?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, agar 99.87% data normal ho aur model sabhi ko 'Normal' predict kar de, toh bhi accuracy 99.87% dikhegi par ek bhi fraud pakad nahi payega! Isliye humne accuracy ko ignore karke <strong>Recall aur Precision-Recall AUC</strong> par model optimize kiya."</div>
            </div>
        </div>
    </div>
</div>

<div class="page-break"></div>

<!-- ========================================== -->
<!-- SLIDE 9 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 9: Smart Features: Tracking the Money Path (The 2 Math Clues)</div>
        <span class="speaker-tag speaker-tayyab">Speaker: Mohammad Tayyab</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                Dono equations ko ratna nahi, logic samajhna hai: Normal transaction mein balance math match karta hai (difference = 0). Fraud mein attacker pura account drain karta hai ya destination spoof hoti hai, toh balance formula break ho jata hai.
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Sir, raw transaction amounts se fraud detect karna impossible hota hai kyunki legit business bhi ₹1 Lakh bhejta hai aur fraudster bhi. Isliye humne do <strong>engineered balance-arithmetic features</strong> develop kiye:"</em></p>
                <ul>
                    <li><em><strong>1. Sender Balance Clue (<span class="code-badge">errorBalanceOrig</span>):</strong><br>
                    Formula: <span class="code-badge">errorBalanceOrig = newbalanceOrig + amount - oldbalanceOrg</span><br>
                    <em>Logic:</em> Normal transaction mein agar aapke paas ₹10,000 hain aur aap ₹2,000 bhejte hain, toh bacha ₹8,000. Math check: 8000 + 2000 - 10000 = <strong>0</strong>. Lekin fraud attack mein hacker pura balance sweep kar deta hai toh balance unexpected drop show karta hai.</em></li>
                    <li><em><strong>2. Receiver Balance Clue (<span class="code-badge">errorBalanceDest</span>):</strong><br>
                    Formula: <span class="code-badge">errorBalanceDest = oldbalanceDest + amount - newbalanceDest</span><br>
                    <em>Logic:</em> Yeh verify karta hai ki receiver ke account mein actual cash deposit hua ya fir zero balance mule account ke through route kiya gaya."</em></li>
                </ul>
                <p><em>"In do mathematical features ne model ke detection recall ko directly <strong>99.57%</strong> tak boost kiya hai."</em></p>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Yeh dono features PaySim dataset mein pehle se the ya aapne engineer kiye?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, yeh raw dataset mein nahi the. Dataset mein sirf `oldbalance` aur `newbalance` the. Yeh dono discrepancy features humne feature engineering step mein mathematical logic se construct kiye hain."</div>
            </div>
        </div>
    </div>
</div>

<!-- ========================================== -->
<!-- SLIDE 10 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 10: ML Model Pipeline Diagram (Offline vs Online)</div>
        <span class="speaker-tag speaker-hasan">Speaker: Mohammad Hasan Rizvi</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                Pipeline do phases mein partitioned hai: Phase 1 (Offline Training - 6.36M data, 80/20 split, XGBoost serialized to joblib) &bull; Phase 2 (Online Inference - Live API, 1.8ms scoring, SHAP explainability).
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Thank you Tayyab."</em></p>
                <p><em>"Sir, is technical architecture mein hamara complete Machine Learning lifecycle do distinct phases mein divided hai:"</em></p>
                <ul>
                    <li><em><strong>Phase 1: Training Phase (Offline):</strong> Humne 6.36 Million PaySim records par data cleaning, label encoding aur hamare 2 balance features apply kiye. 80-20 stratified train-test split karke XGBoost model ko train kiya aur compressed <span class="code-badge">model.joblib</span> aur background SHAP summary files serialize kiye.</em></li>
                    <li><em><strong>Phase 2: Prediction Phase (Online Real-Time):</strong> Jab live payment hit hoti hai, hamara engine without disk re-training direct in-memory model ko call karta hai. Sirf <strong>1.8 milliseconds</strong> ke andar risk score calculate hota hai, TreeSHAP values extract hoti hain, aur Django database mein audit entry commit ho jati hai."</em></li>
                </ul>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Joblib file ka size kitna hai aur kya model ko production mein reload karna padta hai har request par?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, model ka serialized size approx 8.5 MB hai. Django server startup ke waqt `predictor.py` mein yeh memory mein ek baar load ho jata hai (singleton pattern), isliye har transaction prediction par zero loading overhead rehta hai."</div>
            </div>
        </div>
    </div>
</div>

<div class="page-break"></div>

<!-- ========================================== -->
<!-- SLIDE 11 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 11: Why We Chose XGBoost over Others</div>
        <span class="speaker-tag speaker-hasan">Speaker: Mohammad Hasan Rizvi</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                Teacher hamesha puchti hai: "Deep Learning kyun nahi lagaya?" Clear answers: Deep Learning tabular data par slow hai (100ms+), GPU costly hai, aur Black Box hai. Logistic Regression underfit karta hai. XGBoost fastest, highest recall (99.57%) aur 100% explainable hai.
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Sir, humne final model choose karne se pehle teen distinct algorithmic paradigms ko benchmark kiya:"</em></p>
                <ul>
                    <li><em><strong>1. Logistic Regression (Rejected):</strong> Yeh linear hyperplanes use karta hai. Financial fraud highly non-linear hota hai, isliye iska recall bohot poor tha aur false negatives high the.</em></li>
                    <li><em><strong>2. Deep Learning / Neural Networks (Rejected):</strong> Deep Neural Nets images aur text par excel karte hain, lekin structured tabular data par decision trees superior hote hain. DL model inference 100+ ms leti hai, heavy GPUs mangti hai, aur sabse bada issue: yeh 100% 'Black Box' hoti hai.</em></li>
                    <li><em><strong>3. XGBoost (Extreme Gradient Boosting - Selected):</strong> Tabular benchmarks par globally state-of-the-art hai. Non-linear relationships ko microsecond latency (1.8ms) mein evaluate karta hai, CPU par smoothly chalta hai, aur TreeSHAP ke sath natively integrated hai."</em></li>
                </ul>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "XGBoost mein Gradient Boosting ka basic mechanism kya hota hai?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, gradient boosting sequential trees banata hai. Pehla tree data predict karta hai, fir jo errors (residuals) bachte hain, agla tree specifically unhi errors ko minimize karne ke liye train hota hai. Is residual learning se accuracy continuously refine hoti hai."</div>
            </div>
        </div>
    </div>
</div>

<!-- ========================================== -->
<!-- SLIDE 12 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 12: Explainable AI: No Hidden Secrets (TreeSHAP)</div>
        <span class="speaker-tag speaker-hasan">Speaker: Mohammad Hasan Rizvi</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                RBI rules ke mutabiq agar bank customer ka account freeze karega toh legal justification deni hogi. TreeSHAP Cooperative Game Theory par based hai jo har feature ka mathematically exact score contribution nikalta hai.
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Sir, banking industry mein Explainability koi luxury nahi balki <strong>regulatory mandate</strong> hai. Agar bank kisi merchant ya user ka paisa hold par daal de, toh compliance officer yeh nahi keh sakta ki 'hamare deep model ne predict kiya isliye roka'."</em></p>
                <p><em>"Is problem ko solve karne ke liye humne <strong>TreeSHAP (SHapley Additive exPlanations)</strong> integrate kiya hai:"</em></p>
                <ul>
                    <li><em>TreeSHAP cooperative game theory use karke base risk score se individual features ka contribution isolate karta hai.</em></li>
                    <li><em><strong>Red Risk Boosters (+):</strong> Features jo fraud score ko badhate hain (e.g. Account balance ka 100% deplete ho jana: +0.48; Transaction type CASH_OUT hona: +0.22).</em></li>
                    <li><em><strong>Green Safety Signals (-):</strong> Features jo genuine payment indicate karte hain (e.g. Healthy balance maintain hona: -0.18; Normal destination history).</em></li>
                </ul>
                <p><em>"Yeh output ek transparent human-readable report card banata hai jisse compliance officer instantly formal report file kar sakta hai."</em></p>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "SHAP aur standard Feature Importance (MDI) mein kya difference hai?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, feature importance pure model ka *Global* summary batata hai ki training mein kaunsa column important tha. TreeSHAP *Local* hota hai—yeh ek *single specific transaction* ke liye batata hai ki us particular transfer ko fraud kyun declare kiya gaya."</div>
            </div>
        </div>
    </div>
</div>

<div class="page-break"></div>

<!-- ========================================== -->
<!-- SLIDE 13 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 13: Live Simulator: Testing the System</div>
        <span class="speaker-tag speaker-hasan">Speaker: Mohammad Hasan Rizvi</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                Simulator ke 4 presets ka logic pata hona chahiye:
                1. Account Drain (₹2.5L transfer &rarr; sender balance 0 &rarr; 100% Red Block).
                2. Drain + Cash-out (₹1L physical withdrawal &rarr; electronic balance 0 &rarr; 100% Red Block).
                3. Normal Transfer (₹5,000 &rarr; healthy remaining balance &rarr; 0% Green Approved).
                4. Small Cash-out (₹2,000 ATM &rarr; normal balance &rarr; 0% Green Approved).
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Sir, hamare live web interface par humne ek <strong>Interactive Transaction Simulator</strong> deploy kiya hai jisse koi bhi evaluator real-time scenarios live test kar sakta hai:"</em></p>
                <ul>
                    <li><em><strong>Scenario 1: 'Account Drain Attack':</strong> ₹2,50,000 ka unauthorized transfer. Sender balance ₹2.5 Lakh se seedha ₹0 ho jata hai. Evaluate dabate hi dial instantly <strong>100% Red Risk</strong> dikhata hai, transaction block hoti hai aur security alert raise ho jata hai.</em></li>
                    <li><em><strong>Scenario 2: 'Drain + Cash-Out Attack':</strong> Hacker ₹1,00,000 cash out karta hai aur digital balance zero chhodta hai. Yeh bhi 100% risk par intercept hoti hai.</em></li>
                    <li><em><strong>Scenario 3: 'Normal UPI Transfer':</strong> ₹5,000 ka routine peer-to-peer transfer. Sender ke paas ₹75,000 ka healthy balance bachta hai. Dial instantly <strong>0.00% Green (Safe)</strong> dikhata hai aur transaction approve ho jati hai.</em></li>
                </ul>
                <p><em>"Har evaluation ke sath bottom panel par TreeSHAP ke exact factors render hote hain aur transaction database ledger mein save ho jati hai."</em></p>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Cash-out attack mein receiver balance zero kyun dikhaya gaya hai?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, CASH_OUT ka matlab hota hai ATM ya banking correspondent se physical currency note nikal lena. Jab physical cash nikal gaya, toh digital bank ledger mein destination balance 0 bachta hai kyunki cash paper form mein user ke haath mein chala gaya."</div>
            </div>
        </div>
    </div>
</div>

<!-- ========================================== -->
<!-- SLIDE 14 -->
<!-- ========================================== -->
<div class="slide-card">
    <div class="slide-header">
        <div class="slide-title">Slide 14: Research, References & Concluding Remarks</div>
        <span class="speaker-tag speaker-wasil">Speaker: Wasil Ali</span>
    </div>
    <div class="slide-body">
        <div class="section-block">
            <div class="section-label label-concept">💡 Dimag mein kya clear rakhna hai:</div>
            <div class="concept-box">
                Academic grounding acknowledge karni hai: Lopez-Rojas (PaySim benchmark), Chen & Guestrin (XGBoost 2016), Lundberg & Lee (SHAP 2017), RBI guidelines & DPDP Act 2023. Confident finish aur evaluators ko questions ke liye welcome karna.
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-speech">🗣️ Teacher ke samne kya bolna hai:</div>
            <div class="speech-box">
                <p><em>"Sir, hamara poora project verified research papers aur industry-standard frameworks par grounded hai:"</em></p>
                <ul>
                    <li><em><strong>Research Foundations:</strong> PaySim synthetic financial benchmark (Lopez-Rojas et al.), XGBoost gradient boosting framework (Chen & Guestrin, KDD 2016), aur SHAP Unified Explainability (Lundberg & Lee, NeurIPS 2017).</em></li>
                    <li><em><strong>Regulatory Alignment:</strong> Reserve Bank of India (RBI) Real-Time Risk Guidelines aur India's DPDP Act, 2023.</em></li>
                    <li><em><strong>Future Scope:</strong> Aage chalkar hum multi-hop mule networks pakadne ke liye Graph Neural Networks (GNNs) aur high-throughput Kafka streaming pipeline integrate karenge.</em></li>
                </ul>
                <p><em>"Conclusion yeh hai ki FraudGuard prove karta hai ki real-time high-speed payments ko hum bina kisi black-box compromise ke 1.8 milliseconds mein protect kar sakte hain."</em></p>
                <p><em>"Thank you so much Sajid Sir, Ruchi Ma'am, and all respected evaluators. We are now open for your questions."</em></p>
            </div>
        </div>
        <div class="section-block">
            <div class="section-label label-viva">❓ Expected Cross-Question & Quick Defense:</div>
            <div class="viva-box">
                <div class="viva-q">Teacher: "Aapke project ka practical deployment plan kya hoga agar kisi real bank ko dena ho?"</div>
                <div class="viva-a"><strong>👉 Winning Jawab:</strong> "Sir, hum ise containerized Docker microservice ki tarah deploy karenge jo bank ke transaction switch (jaise NPCI UPI Switch) ke parallel chalegi. Kafka queue se transactions stream hongi aur sub-2ms mein risk score return hoga."</div>
            </div>
        </div>
    </div>
</div>

<!-- ========================================== -->
<!-- GOLDEN RULES BOX -->
<!-- ========================================== -->
<div class="golden-rules">
    <h3>🏆 Final Presentation Defense &mdash; 3 Golden Rules:</h3>
    <ol>
        <li><strong>Confidence & Flow:</strong> Kisi bhi evaluator ke samne nervous nahi hona hai. Aap sabhi ko system ka ek-ek formula, architecture aur code pata hai.</li>
        <li><strong>Formula Defence:</strong> Agar teacher Slide 9 par pahuche, toh simple words mein kehna: <em>"Ma'am, genuine transfer mein sender ka balance ghat kar amount jitna match hota hai (error = 0). Fraud mein attacker account pura empty kar deta hai toh math break ho jata hai."</em> Yeh bolte hi teacher impress ho jayegi.</li>
        <li><strong>Evaluation Metric Trick:</strong> Agar teacher puche <em>"Accuracy kitni hai?"</em>, toh turant kehna: <em>"Ma'am, financial fraud mein accuracy ek mathematical trap hoti hai kyunki 99.87% data legit hai. Isliye humne <strong>Recall (99.57%) aur F1-Score (99.18%)</strong> par benchmark kiya hai."</em> &mdash; Is point par teacher full marks degi!</li>
    </ol>
</div>

</body>
</html>
"""

# Write HTML file
html_path = r"c:\Users\aliwa\fraudguard\ppt_hinglish_guide.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML successfully generated at: {html_path}")

# Compile to PDF using headless Edge
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
pdf_path = r"c:\Users\aliwa\fraudguard\FraudGuard_PPT_Presentation_Hinglish_Guide.pdf"

cmd = [
    edge_exe,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    f"file:///{html_path.replace(os.sep, '/')}"
]

print("Compiling to PDF with Microsoft Edge...")
result = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(pdf_path):
    size_kb = os.path.getsize(pdf_path) / 1024
    print(f"SUCCESS: PDF created at {pdf_path} ({size_kb:.1f} KB)")
else:
    print(f"FAILED: PDF not found. Output: {result.stdout} Error: {result.stderr}")
