import { useFonts } from 'expo-font';
import { Prata_400Regular } from '@expo-google-fonts/prata';
import { Figtree_400Regular, Figtree_600SemiBold, Figtree_700Bold } from '@expo-google-fonts/figtree';

/** True once the Ask Remetra fonts are ready (or failed, so the UI still renders). */
export function useAskFonts(): boolean {
  const [loaded, error] = useFonts({ Prata_400Regular, Figtree_400Regular, Figtree_600SemiBold, Figtree_700Bold });
  return loaded || Boolean(error);
}
