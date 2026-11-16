import { useState } from 'react';
import { Text, View } from 'react-native';
import * as Clipboard from 'expo-clipboard';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import { ButtonRow, CardShell, CardTitle, ErrorNote, Eyebrow } from './CardParts';
import { PillButton } from '../PillButton';
import type { ChatCard } from '../../../types/chat';

type SummaryCardData = Extract<ChatCard, { type: 'summary' }>;

const escapeHtml = (value: string) =>
  value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export function summaryToText(card: SummaryCardData): string {
  return [
    card.title,
    ...card.sections.map((section) => `${section.title.toUpperCase()}\n${section.body}`),
    card.disclaimer,
  ].join('\n\n');
}

function summaryToHtml(card: SummaryCardData): string {
  const sections = card.sections
    .map((section) => `<h2>${escapeHtml(section.title)}</h2><p>${escapeHtml(section.body)}</p>`)
    .join('');
  return `<!DOCTYPE html><html><head><meta charset="utf-8" /><style>
    body { font-family: -apple-system, Helvetica, Arial, sans-serif; color: #3b2a24; padding: 32px; }
    .eyebrow { font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #7a7068; }
    h1 { font-family: Georgia, serif; font-weight: normal; font-size: 24px; margin: 4px 0 24px; }
    h2 { font-size: 11px; letter-spacing: 0.04em; text-transform: uppercase; color: #92472a; margin: 16px 0 4px; }
    p { font-size: 14px; line-height: 1.45; color: #6e5a50; margin: 0; }
    .disclaimer { border-top: 1px solid #f4f0ec; margin-top: 24px; padding-top: 12px; font-size: 12px; color: #7a7068; }
  </style></head><body>
    <div class="eyebrow">${escapeHtml(card.eyebrow)}</div>
    <h1>${escapeHtml(card.title)}</h1>
    ${sections}
    <p class="disclaimer">${escapeHtml(card.disclaimer)}</p>
  </body></html>`;
}

/** Figma "Ask / Dietitian summary" (screen 08). */
export function SummaryCard({ card, onCopied }: { card: SummaryCardData; onCopied: () => void }) {
  const [sharing, setSharing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const shareAsPdf = async () => {
    setSharing(true);
    setError(null);
    try {
      const { uri } = await Print.printToFileAsync({ html: summaryToHtml(card) });
      if (!(await Sharing.isAvailableAsync())) throw new Error('Sharing unavailable');
      await Sharing.shareAsync(uri, { mimeType: 'application/pdf', UTI: 'com.adobe.pdf', dialogTitle: card.title });
    } catch {
      setError('Couldn’t create the PDF. Try copying the text instead.');
    } finally {
      setSharing(false);
    }
  };

  const copyText = async () => {
    setError(null);
    try {
      await Clipboard.setStringAsync(summaryToText(card));
      onCopied();
    } catch {
      setError('Couldn’t copy the summary. Please try again.');
    }
  };

  return (
    <CardShell>
      <View className="gap-0.5">
        <Eyebrow>{card.eyebrow}</Eyebrow>
        <CardTitle>{card.title}</CardTitle>
      </View>
      {card.sections.map((section) => (
        <View key={section.title} className="gap-0.5">
          <Text className="font-figtree-bold text-[11px] uppercase tracking-[0.44px] text-remetra-chip-strong">
            {section.title}
          </Text>
          <Text className="font-figtree text-[13px] leading-[18px] text-remetra-text-secondary">{section.body}</Text>
        </View>
      ))}
      <Text className="border-t border-remetra-line-subtle pt-[7px] font-figtree text-[12px] leading-4 text-remetra-text-tertiary">
        {card.disclaimer}
      </Text>
      {error && <ErrorNote>{error}</ErrorNote>}
      <ButtonRow>
        <PillButton label={sharing ? 'Preparing…' : 'Share as PDF'} onPress={shareAsPdf} disabled={sharing} fill />
        <PillButton label="Copy text" onPress={copyText} variant="ghost" fill />
      </ButtonRow>
    </CardShell>
  );
}
