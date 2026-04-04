import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { BackgroundGradient } from '../../components/BackgroundGradient';
import { useBankStore } from '../../store/bankStore';
import { symptomLogService } from '../../api/symptom_log_service';
import { algorithmService } from '../../api/algorithm_service';
import { useAuthStore } from '../../store/useAuthStore';
import { useAppNavigation } from '../../navigation/hooks';

interface SymptomCount {
  symptomId: string;
  name: string;
  location: string;
  sensation: string;
  count: number;
}

export function AnalysisScreen() {
  const { symptoms, fetchSymptoms } = useBankStore();
  const username = useAuthStore((s) => s.user.name);
  const [symptomCounts, setSymptomCounts] = useState<SymptomCount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        await fetchSymptoms();
        const logs = await symptomLogService.getMySymptomLogs();

        const countMap: Record<string, number> = {};
        for (const log of logs) {
          countMap[log.symptom_id] = (countMap[log.symptom_id] ?? 0) + 1;
        }

        const counts: SymptomCount[] = useBankStore
          .getState()
          .symptoms.map((s) => ({
            symptomId: s.id,
            name: s.name,
            location: s.location,
            sensation: s.sensation,
            count: countMap[s.id] ?? 0,
          }))
          .filter((s) => s.count > 0)
          .sort((a, b) => b.count - a.count);

        setSymptomCounts(counts);

        // Pre-run the algorithm for all logged symptoms so the detail screen has data ready
        const loggedSymptomIds = counts.map((s) => s.symptomId);
        if (loggedSymptomIds.length > 0 && username) {
          algorithmService
            .analyze({ user_id: username, symptom_ids: loggedSymptomIds })
            .catch(() => {}); // fire-and-forget; failures are non-blocking
        }
      } catch (err: any) {
        setError(err.message ?? 'Failed to load analysis');
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  return (
    <View style={{ flex: 1 }}>
      <BackgroundGradient />
      <ScrollView contentContainerStyle={{ flexGrow: 1, padding: 24, paddingTop: 64 }}>
        <Text
          style={{
            fontSize: 24,
            fontWeight: '600',
            color: '#b2939b',
            fontStyle: 'italic',
            letterSpacing: 1,
            textAlign: 'center',
            marginBottom: 32,
          }}
        >
          YOUR ANALYSIS
        </Text>

        <SectionDivider label="Symptoms by Occurrences" />

        {loading ? (
          <ActivityIndicator color="#b2939b" style={{ marginTop: 32 }} />
        ) : error ? (
          <Text style={{ color: '#B8624F', textAlign: 'center', marginTop: 24 }}>{error}</Text>
        ) : symptomCounts.length === 0 ? (
          <Text style={{ color: '#aaa', textAlign: 'center', marginTop: 24, fontSize: 14 }}>
            No symptoms logged yet.
          </Text>
        ) : (
          <View style={{ gap: 10 }}>
            {symptomCounts.map((item, index) => (
              <SymptomRow key={item.symptomId} rank={index + 1} item={item} />
            ))}
          </View>

        )}
      </ScrollView>
    </View>
  );
}

function SectionDivider({ label }: { label: string }) {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
      <Text style={{ fontSize: 12, fontWeight: '700', color: '#aaa', marginRight: 8, letterSpacing: 1 }}>
        {label.toUpperCase()}
      </Text>
      <View style={{ flex: 1, height: 1, backgroundColor: '#E5E5E5' }} />
    </View>
  );
}

function SymptomRow({ rank, item }: { rank: number; item: SymptomCount }) {
  const navigation = useAppNavigation();
  const subtitle = [item.location, item.sensation].filter(Boolean).join(' · ');

  return (
    <TouchableOpacity
      onPress={() => navigation.navigate('SymptomDetail', { symptomId: item.symptomId, symptomName: item.name })}
      style={{
        backgroundColor: 'rgba(255,255,255,0.35)',
        borderRadius: 12,
        padding: 16,
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
      }}
    >
      <Text style={{ fontSize: 14, fontWeight: '700', color: '#b2939b', width: 24, textAlign: 'center' }}>
        {rank}
      </Text>
      <View style={{ flex: 1 }}>
        <Text style={{ fontSize: 15, color: '#444', fontWeight: '600' }}>{item.name}</Text>
        {subtitle ? (
          <Text style={{ fontSize: 12, color: '#aaa', marginTop: 2 }}>{subtitle}</Text>
        ) : null}
      </View>
      <View
        style={{
          backgroundColor: '#F8B4A8',
          borderRadius: 20,
          paddingHorizontal: 10,
          paddingVertical: 4,
          minWidth: 36,
          alignItems: 'center',
        }}
      >
        <Text style={{ fontSize: 14, fontWeight: '700', color: '#7B3B4E' }}>{item.count}</Text>
      </View>
      <Text style={{ fontSize: 18, color: '#ccc' }}>›</Text>
    </TouchableOpacity>
  );
}
