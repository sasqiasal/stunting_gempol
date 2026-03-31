/**
 * Test Frontend Evaluasi Response Parsing
 * Memverifikasi bahwa frontend dapat mengparse response dari backend dengan benar
 */

// Mock response dari backend
const mockBackendResponse = {
  status: "success",
  message: "Model performance evaluation completed",
  dataset_info: {
    source: "CSV data_latih_stunting.csv",
    total_samples: 500,
    train_size: 400,
    test_size: 100,
    split_method: "stratified 80/20"
  },
  confusion_matrix: {
    labels: ["Normal & Gizi Baik", "Normal & Kurang Gizi", "Stunting & Gizi Baik", "Stunting & Kurang Gizi"],
    matrix: [[30, 5, 2, 0], [3, 28, 0, 1], [1, 0, 25, 3], [0, 2, 2, 26]]
  },
  metrics: {
    accuracy: 0.8533,
    accuracy_percentage: 85.33,
    macro_avg_precision: 0.8506,
    macro_avg_precision_percentage: 85.06,
    macro_avg_recall: 0.8533,
    macro_avg_recall_percentage: 85.33,
    macro_avg_f1: 0.8519,
    macro_avg_f1_percentage: 85.19,
    per_class: {
      "0": { label: "Normal & Gizi Baik", precision: 0.8571, recall: 0.8571, f1_score: 0.8571, support: 37 },
      "1": { label: "Normal & Kurang Gizi", precision: 0.7368, recall: 0.9032, f1_score: 0.8125, support: 31 },
      "2": { label: "Stunting & Gizi Baik", precision: 0.8929, recall: 0.8065, f1_score: 0.8462, support: 31 },
      "3": { label: "Stunting & Kurang Gizi", precision: 0.8667, recall: 0.8387, f1_score: 0.8525, support: 31 }
    }
  },
  k_comparisons: [
    {
      k: 3,
      accuracy: 1.0,
      precision: 1.0,
      recall: 1.0,
      specificity: 1.0,
      f1_score: 1.0,
      tp: 50,
      tn: 50,
      fp: 0,
      fn: 0
    },
    {
      k: 5,
      accuracy: 0.98,
      precision: 0.98,
      recall: 0.96,
      specificity: 0.99,
      f1_score: 0.97,
      tp: 48,
      tn: 49,
      fp: 1,
      fn: 2
    },
    {
      k: 7,
      accuracy: 0.96,
      precision: 0.95,
      recall: 0.94,
      specificity: 0.97,
      f1_score: 0.945,
      tp: 47,
      tn: 48,
      fp: 2,
      fn: 3
    },
    {
      k: 9,
      accuracy: 0.94,
      precision: 0.92,
      recall: 0.92,
      specificity: 0.96,
      f1_score: 0.92,
      tp: 46,
      tn: 48,
      fp: 4,
      fn: 2
    }
  ],
  sample_explanations: []
};

// Test: Parse response seperti yang dilakukan frontend
console.log("Testing Frontend Response Parsing...\n");

const data = mockBackendResponse;

if (data?.k_comparisons && Array.isArray(data.k_comparisons)) {
  console.log("✓ k_comparisons found and is an array");
  console.log(`✓ Number of K values: ${data.k_comparisons.length}\n`);

  // Format k_comparisons ke struktur frontend
  const formattedKComparisons = {
    comparisons: data.k_comparisons.map(k => ({
      k_value: k.k,
      metrics: {
        accuracy: k.accuracy,
        accuracy_pct: Math.round(k.accuracy * 100),
        precision: k.precision,
        precision_pct: Math.round(k.precision * 100),
        recall: k.recall,
        recall_pct: Math.round(k.recall * 100),
        specificity: k.specificity || 0,
        specificity_pct: Math.round((k.specificity || 0) * 100),
        f1_score: k.f1_score,
        f1_pct: Math.round(k.f1_score * 100)
      },
      confusion_matrix: {
        tp: k.tp || 0,
        tn: k.tn || 0,
        fp: k.fp || 0,
        fn: k.fn || 0
      }
    })),
    recommendation: data.k_comparisons.length > 0 ? {
      best_k: data.k_comparisons.reduce((max, curr) => curr.f1_score > max.f1_score ? curr : max).k,
      f1_score: Math.max(...data.k_comparisons.map(k => k.f1_score))
    } : null,
    dataset_info: data.dataset_info
  };

  console.log("✓ Formatted k_comparisons successfully\n");

  // Test: akses data untuk setiap K value
  formattedKComparisons.comparisons.forEach(comp => {
    console.log(`K=${comp.k_value}:`);
    console.log(`  Metrics: Acc=${comp.metrics.accuracy_pct}%, Prec=${comp.metrics.precision_pct}%, Rec=${comp.metrics.recall_pct}%, F1=${comp.metrics.f1_pct}%`);
    console.log(`  Confusion Matrix: TP=${comp.confusion_matrix.tp}, TN=${comp.confusion_matrix.tn}, FP=${comp.confusion_matrix.fp}, FN=${comp.confusion_matrix.fn}`);
    
    // Verify TP/TN/FP/FN values are not all 0
    const hasValues = comp.confusion_matrix.tp > 0 || comp.confusion_matrix.tn > 0 || comp.confusion_matrix.fp > 0 || comp.confusion_matrix.fn > 0;
    if (hasValues) {
      console.log(`  ✓ Confusion matrix has valid values`);
    } else {
      console.log(`  ✗ WARNING: All TP/TN/FP/FN are 0`);
    }
  });

  console.log(`\n✓ Best K: ${formattedKComparisons.recommendation.best_k} (F1=${formattedKComparisons.recommendation.f1_score})`);
  console.log("\n✓ All frontend parsing tests passed!");
} else {
  console.log("✗ ERROR: k_comparisons not found or is not an array");
}
