const toPdfText = (value) => String(value ?? '')
  .normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '')
  .replace(/[^\x20-\x7E]/g, ' ')
  .replace(/\\/g, '\\\\')
  .replace(/\(/g, '\\(')
  .replace(/\)/g, '\\)');

const wrapText = (value, maxLength = 88) => {
  const words = String(value ?? '').split(/\s+/).filter(Boolean);
  const lines = [];
  let line = '';

  words.forEach((word) => {
    if (!line) {
      line = word;
    } else if (`${line} ${word}`.length <= maxLength) {
      line += ` ${word}`;
    } else {
      lines.push(line);
      line = word;
    }
  });
  if (line) lines.push(line);
  return lines.length ? lines : [''];
};

const formatCurrency = (value) => {
  if (value == null || !Number.isFinite(Number(value))) return 'Not recorded';
  return `INR ${new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(Number(value))}`;
};

const createReportContent = (application, prediction) => {
  const pages = [];
  let commands;
  let y;

  const startPage = () => {
    commands = [];
    pages.push(commands);
    y = 748;
    commands.push('0.035 0.52 0.68 rg');
    commands.push(`BT /F2 20 Tf 54 ${y} Td (CREDXAI) Tj ET`);
    y -= 25;
    commands.push('0.10 0.15 0.23 rg');
    commands.push(`BT /F2 13 Tf 54 ${y} Td (Applicant Assessment Report) Tj ET`);
    y -= 12;
    commands.push('0.72 0.78 0.84 RG 0.7 w 54 700 m 558 700 l S');
    y = 682;
  };

  const addText = (value, { size = 10, bold = false, color = '0.12 0.17 0.24' } = {}) => {
    wrapText(value).forEach((line) => {
      if (y < 62) startPage();
      commands.push(`${color} rg`);
      commands.push(`BT /${bold ? 'F2' : 'F1'} ${size} Tf 54 ${y} Td (${toPdfText(line)}) Tj ET`);
      y -= size + 5;
    });
  };

  const addSection = (title) => {
    if (y < 88) startPage();
    y -= 7;
    addText(title, { size: 12, bold: true, color: '0.035 0.42 0.58' });
    y -= 2;
  };

  startPage();
  addText(`Application #${application.id}`, { size: 15, bold: true });
  const createdAt = application.createdAt ? new Date(application.createdAt).toLocaleString() : 'Not recorded';
  addText(`Assessment date: ${createdAt}`);

  addSection('Assessment result');
  const probability = prediction.default_probability_percent != null && Number.isFinite(Number(prediction.default_probability_percent))
    ? Number(prediction.default_probability_percent)
    : prediction.default_probability != null && Number.isFinite(Number(prediction.default_probability))
      ? Number(prediction.default_probability) * 100
      : null;
  if (probability == null) throw new Error('The saved assessment does not contain a valid model probability.');
  addText(`Adverse-outcome probability: ${probability.toFixed(2)}%`, { size: 13, bold: true });
  addText(`Risk category: ${prediction.risk_band || 'Not returned'}`, { bold: true });
  addText(`Model used: ${prediction.model_type || application.modelType || 'Not recorded'}`);
  addText(`Model version: ${application.modelVersion || prediction.model_version || 'Unversioned'}`);
  addText(`Application status: ${application.status || 'Not recorded'}`);

  addSection('Application details');
  addText(`Requested loan amount: ${formatCurrency(application.loanAmount)}`);
  addText(`Loan purpose: ${application.purpose || 'Not recorded'}`);
  addText(`Existing monthly debt: ${formatCurrency(application.existingMonthlyDebt)}`);
  addText(`Self-reported repayment history: ${(application.repaymentHistory || 'UNKNOWN').replaceAll('_', ' ')}`);

  const increasing = Array.isArray(prediction.risk_increasing_factors) ? prediction.risk_increasing_factors : [];
  const reducing = Array.isArray(prediction.risk_reducing_factors) ? prediction.risk_reducing_factors : [];
  const explanations = Array.isArray(prediction.explanation)
    ? prediction.explanation
    : (typeof prediction.explanation === 'string' ? [prediction.explanation] : []);

  addSection('Model explanation');
  if (explanations.length) explanations.forEach((explanation) => addText(`- ${explanation}`));
  else addText('The saved model response did not include a natural-language explanation.');

  addSection('Risk-increasing factors');
  if (increasing.length) {
    increasing.forEach((factor) => {
      const contribution = Number(factor?.contribution);
      addText(`${factor?.feature || 'Unnamed factor'}: ${Number.isFinite(contribution) ? `${contribution > 0 ? '+' : ''}${contribution.toFixed(4)}` : 'Contribution not provided'}`);
    });
  } else addText('No risk-increasing factors were returned by the model.');

  addSection('Risk-reducing factors');
  if (reducing.length) {
    reducing.forEach((factor) => {
      const contribution = Number(factor?.contribution);
      addText(`${factor?.feature || 'Unnamed factor'}: ${Number.isFinite(contribution) ? `${contribution > 0 ? '+' : ''}${contribution.toFixed(4)}` : 'Contribution not provided'}`);
    });
  } else addText('No risk-reducing factors were returned by the model.');

  addSection('Important information');
  if (prediction.disclaimer) addText(prediction.disclaimer);
  addText('CredXAI is a decision-support prototype. This model estimate and its risk category are not a lending decision or a guarantee.');

  return pages;
};

const buildPdfBlob = (pages) => {
  const objects = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>',
  ];
  const pageRefs = [];

  pages.forEach((pageCommands) => {
    const pageId = objects.length + 1;
    const contentId = pageId + 1;
    pageRefs.push(`${pageId} 0 R`);
    const pageNumber = pageRefs.length;
    pageCommands.push(`0.45 0.50 0.56 rg BT /F1 8 Tf 54 32 Td (CredXAI assessment | Application record | Page ${pageNumber}) Tj ET`);
    const content = pageCommands.join('\n');
    objects.push(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents ${contentId} 0 R >>`);
    objects.push(`<< /Length ${content.length} >>\nstream\n${content}\nendstream`);
  });

  objects[1] = `<< /Type /Pages /Kids [${pageRefs.join(' ')}] /Count ${pageRefs.length} >>`;
  let pdf = '%PDF-1.4\n';
  const offsets = [0];
  objects.forEach((object, index) => {
    offsets.push(pdf.length);
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });
  const xrefOffset = pdf.length;
  pdf += `xref\n0 ${offsets.length}\n0000000000 65535 f \n`;
  offsets.slice(1).forEach((offset) => { pdf += `${String(offset).padStart(10, '0')} 00000 n \n`; });
  pdf += `trailer\n<< /Size ${offsets.length} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;
  return new Blob([pdf], { type: 'application/pdf' });
};

export const createAssessmentPdf = (application) => {
  if (!application?.id || !application.predictionDetails) {
    throw new Error('This saved application does not include the prediction details needed for a complete report.');
  }

  let prediction;
  try {
    prediction = JSON.parse(application.predictionDetails);
  } catch {
    throw new Error('The saved prediction details could not be read.');
  }

  return buildPdfBlob(createReportContent(application, prediction));
};

export const downloadAssessmentPdf = (application) => {
  const pdfBlob = createAssessmentPdf(application);
  const url = URL.createObjectURL(pdfBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `CredXAI-Assessment-${application.id}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};
