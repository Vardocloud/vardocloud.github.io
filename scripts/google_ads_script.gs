/**
 * Google Ads → Vanitas Rapor Scripti
 * 
 * NE YAPAR:
 * - Günlük kampanya performansını sorgular
 * - Search term verilerini alır
 * - Budget ve harcama durumunu raporlar
 * - E-posta ile Vanitas'a gönderir
 * 
 * NASIL KURULUR:
 * 1. Google Ads hesabında: Araçlar > Scripts > Yeni Script
 * 2. Bu kodun tamamını yapıştır
 * 3. "isimgorulsunn@gmail.com" yerine kendi Gmail'ini yaz
 * 4. Çalışma sıklığını "Günlük" (sabah 09:00) yap
 * 5. "Önizleme" ile test et
 * 6. "Kaydet" ve schedule et
 */

function main() {
  var recipient = "isimgorulsunn@gmail.com";
  var today = new Date();
  var dateStr = Utilities.formatDate(today, "Europe/Istanbul", "yyyy-MM-dd");
  
  var rapor = "📊 Google Ads Günlük Rapor (" + dateStr + ")\n\n";
  rapor += "── KAMPANYA PERFORMANSI ──\n";
  
  // 1. Campaign Performansı
  var campaignReport = AdsApp.report(
    "SELECT campaign.name, campaign.status, " +
    "metrics.impressions, metrics.clicks, metrics.ctr, " +
    "metrics.average_cpc, metrics.cost_micros, " +
    "metrics.conversions, metrics.conversions_value, " +
    "metrics.average_position " +
    "FROM campaign " +
    "WHERE segments.date DURING YESTERDAY " +
    "ORDER BY metrics.cost_micros DESC"
  );
  
  var rows = campaignReport.rows();
  var totalCost = 0, totalImpressions = 0, totalClicks = 0, totalConversions = 0;
  
  while (rows.hasNext()) {
    var row = rows.next();
    var name = row["campaign.name"];
    var status = row["campaign.status"];
    var impressions = parseInt(row["metrics.impressions"]) || 0;
    var clicks = parseInt(row["metrics.clicks"]) || 0;
    var ctr = parseFloat(row["metrics.ctr"]) || 0;
    var cpc = parseFloat(row["metrics.average_cpc"]) || 0;
    var cost = parseFloat(row["metrics.cost_micros"]) / 1000000 || 0;
    var conversions = parseFloat(row["metrics.conversions"]) || 0;
    var convValue = parseFloat(row["metrics.conversions_value"]) || 0;
    
    totalCost += cost;
    totalImpressions += impressions;
    totalClicks += clicks;
    totalConversions += conversions;
    
    rapor += "\n• " + name + " [" + status + "]\n";
    rapor += "  Gösterim: " + impressions.toLocaleString() + " | Tıklama: " + clicks.toLocaleString();
    rapor += " | CTR: %" + ctr.toFixed(2) + "\n";
    rapor += "  Harcama: $" + cost.toFixed(2) + " | CPC: $" + cpc.toFixed(2);
    if (conversions > 0) {
      rapor += " | Dönüşüm: " + conversions + " ($" + convValue.toFixed(2) + ")";
    }
    rapor += "\n";
  }
  
  // 2. Özet
  rapor += "\n── ÖZET ──\n";
  rapor += "Toplam Harcama: $" + totalCost.toFixed(2) + "\n";
  rapor += "Toplam Gösterim: " + totalImpressions.toLocaleString() + "\n";
  rapor += "Toplam Tıklama: " + totalClicks.toLocaleString() + "\n";
  rapor += "Genel CTR: %" + ((totalImpressions > 0) ? (totalClicks / totalImpressions * 100).toFixed(2) : "0.00") + "\n";
  
  var avgCPC = totalClicks > 0 ? totalCost / totalClicks : 0;
  rapor += "Ortalama CPC: $" + avgCPC.toFixed(2) + "\n";
  rapor += "Toplam Dönüşüm: " + totalConversions + "\n";
  
  // 3. Search Term Analizi (ilk 10)
  rapor += "\n── EN ÇOK HARCAMA YAPILAN SEARCH TERMLER ──\n";
  try {
    var searchReport = AdsApp.report(
      "SELECT search_term_view.search_term, " +
      "metrics.impressions, metrics.clicks, metrics.ctr, " +
      "metrics.cost_micros, metrics.conversions " +
      "FROM search_term_view " +
      "WHERE segments.date DURING YESTERDAY AND metrics.impressions > 0 " +
      "ORDER BY metrics.cost_micros DESC " +
      "LIMIT 10"
    );
    
    var sRows = searchReport.rows();
    var count = 0;
    while (sRows.hasNext()) {
      count++;
      var sr = sRows.next();
      var term = sr["search_term_view.search_term"];
      var sCost = (parseInt(sr["metrics.cost_micros"]) || 0) / 1000000;
      var sImpressions = parseInt(sr["metrics.impressions"]) || 0;
      var sClicks = parseInt(sr["metrics.clicks"]) || 0;
      rapor += "\n" + count + ". \"" + term + "\"\n";
      rapor += "   $" + sCost.toFixed(2) + " | " + sImpressions + " gösterim | " + sClicks + " tıklama\n";
    }
  } catch (e) {
    rapor += "(Search term verisi alınamadı)\n";
  }
  
  // 4. Budget Durumu
  rapor += "\n── BUDGET DURUMU ──\n";
  try {
    var budgetReport = AdsApp.report(
      "SELECT campaign.name, campaign_budget.amount_micros, " +
      "metrics.cost_micros " +
      "FROM campaign " +
      "WHERE segments.date DURING YESTERDAY AND campaign.status = 'ENABLED'"
    );
    
    var bRows = budgetReport.rows();
    while (bRows.hasNext()) {
      var br = bRows.next();
      var bName = br["campaign.name"];
      var bBudget = (parseInt(br["campaign_budget.amount_micros"]) || 0) / 1000000;
      var bCost = (parseInt(br["metrics.cost_micros"]) || 0) / 1000000;
      var bPct = bBudget > 0 ? (bCost / bBudget * 100).toFixed(1) : "0.0";
      rapor += "\n• " + bName + ": $" + bCost.toFixed(2) + " / $" + bBudget.toFixed(2) + " (%" + bPct + ")";
    }
  } catch (e) {
    rapor += "(Budget verisi alınamadı)\n";
  }
  
  // 5. Trend Karşılaştırması (önceki gün)
  rapor += "\n\n── ÖNCEKİ GÜNE GÖRE DEĞİŞİM ──\n";
  try {
    var trendReport = AdsApp.report(
      "SELECT metrics.impressions, metrics.clicks, " +
      "metrics.cost_micros " +
      "FROM campaign " +
      "WHERE segments.date DURING YESTERDAY"
    );
    
    var trendReportPrev = AdsApp.report(
      "SELECT metrics.impressions, metrics.clicks, " +
      "metrics.cost_micros " +
      "FROM campaign " +
      "WHERE segments.date DURING LAST_7_DAYS " +
      "AND segments.date != '" + dateStr + "'"
    );
    
    // Önceki 7 günün ortalamasını hesapla (dün hariç)
    var prevTotal = 0, prevDays = 0;
    var pRows = trendReportPrev.rows();
    while (pRows.hasNext()) {
      var pr = pRows.next();
      prevTotal += (parseInt(pr["metrics.cost_micros"]) || 0);
      prevDays++;
    }
    
    if (prevDays > 0) {
      var prevAvg = (prevTotal / prevDays) / 1000000;
      var change = prevAvg > 0 ? ((totalCost - prevAvg) / prevAvg * 100).toFixed(1) : "0.0";
      rapor += "Dünkü harcama: $" + totalCost.toFixed(2) + "\n";
      rapor += "7 günlük ortalama: $" + prevAvg.toFixed(2) + "\n";
      rapor += "Değişim: %" + change + "\n";
    }
  } catch (e) {
    rapor += "(Trend verisi alınamadı)\n";
  }
  
  rapor += "\n── RAPOR SONU ──\n";
  rapor += "Vanitas'ın yorumlaması için gönderildi.";
  
  // E-posta gönder
  MailApp.sendEmail({
    to: recipient,
    subject: "📊 Google Ads Rapor - " + dateStr,
    body: rapor
  });
}
