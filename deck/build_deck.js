const pptxgen = require('pptxgenjs');
const fs = require('fs');

async function main() {
  const manifestPath = process.argv[2];
  const outputPath = process.argv[3];
  if (!manifestPath || !outputPath) {
    throw new Error('Usage: node deck/build_deck.js manifest.json output.pptx');
  }
  const data = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_WIDE';
  pptx.author = 'BriefForge';
  pptx.subject = 'AI-assisted computer science news briefing';
  pptx.title = data.title || 'Computer Science News Briefing';
  pptx.company = 'BriefForge';
  pptx.theme = { headFontFace: 'Vazirmatn', bodyFontFace: 'Vazirmatn', lang: 'fa-IR' };

  pptx.defineSlideMaster({
    title: 'BRIEFFORGE',
    background: { color: '101C2A' },
    objects: [
      { rect: { x: 0, y: 6.92, w: 13.333, h: 0.58, fill: { color: '07111D', transparency: 15 }, line: { color: '07111D', transparency: 100 } } },
      { text: { text: 'BRIEFFORGE  •  COMPUTER SCIENCE NEWS', options: { x: 0.55, y: 7.08, w: 8.5, h: 0.18, fontFace: 'Aptos', fontSize: 8, color: 'A8C5D1', charSpacing: 1.2, margin: 0 } } },
      { text: { text: data.edition_date || '', options: { x: 10.3, y: 7.06, w: 2.45, h: 0.2, fontFace: 'Aptos', fontSize: 8, color: 'A8C5D1', align: 'right', margin: 0 } } }
    ],
    slideNumber: { x: 12.85, y: 7.06, color: 'A8C5D1', fontFace: 'Aptos', fontSize: 8 }
  });

  for (const [index, item] of data.slides.entries()) {
    const slide = pptx.addSlide('BRIEFFORGE');
    slide.background = { color: '101C2A' };
    if (!item.image_path || !fs.existsSync(item.image_path)) {
      throw new Error(`Missing image for slide ${index + 1}: ${item.image_path}`);
    }
    slide.addImage({ path: item.image_path, x: 0, y: 0, w: 13.333, h: 7.5, sizing: 'cover' });
    slide.addShape(pptx.ShapeType.rect, {
      x: 0, y: 0, w: 13.333, h: 7.5,
      line: { color: '07111D', transparency: 100 },
      fill: { color: '07111D', transparency: 38 }
    });
    const opening = index === 0;
    slide.addText(item.title || `Slide ${index + 1}`, {
      x: 0.8, y: opening ? 2.25 : 2.65, w: 11.6, h: 1.15,
      fontFace: 'Vazirmatn', fontSize: opening ? 34 : 30, rtlMode: true,
      bold: true, color: 'FFFFFF', margin: 0.04, valign: 'mid', fit: 'shrink'
    });
    if (item.subtitle) {
      slide.addText(item.subtitle, {
        x: 0.84, y: opening ? 3.55 : 3.78, w: 10.8, h: 0.55,
        fontFace: 'Vazirmatn', fontSize: 17, rtlMode: true, color: 'BDEDE8',
        margin: 0.02, fit: 'shrink'
      });
    }

    const notes = [`SLIDE ${index + 1}: ${item.title || ''}`, '', 'SPEAKING SCRIPT',
      item.narration || 'No narration was generated.'];
    if (item.key_facts && item.key_facts.length) {
      notes.push('', 'KEY FACTS');
      item.key_facts.forEach((x, i) => notes.push(`${i + 1}. ${x}`));
    }
    if (item.technical_context && item.technical_context.length) {
      notes.push('', 'TECHNICAL CONTEXT / CAVEATS');
      item.technical_context.forEach((x, i) => notes.push(`${i + 1}. ${x}`));
    }
    if (item.sources && item.sources.length) {
      notes.push('', 'SOURCES');
      item.sources.forEach((s, i) => notes.push(`${i + 1}. ${s.label || 'Source'}: ${s.url || ''}`));
    }
    if (item.transition) notes.push('', 'TRANSITION', item.transition);
    notes.push('', 'EDITORIAL NOTE: Verify important claims against linked original sources before presenting.');
    slide.addNotes(notes.join('\n'));
  }
  await pptx.writeFile({ fileName: outputPath });
  console.log(`Created ${outputPath}`);
}
main().catch(err => { console.error(err); process.exit(1); });
