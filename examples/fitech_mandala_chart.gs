/**
 * Fitech Mandala Chart (Open Window 64) Generator
 *
 * 株式会社ファイテック 代表取締役 林 富徳
 * 大目標: 世界一の消火剤メーカーになる
 *
 * 使い方:
 *   1. 対象の Google スプレッドシートを開く
 *   2. メニュー「拡張機能」>「Apps Script」を開く
 *   3. 既存コードを削除し、本ファイルの内容を貼り付け
 *   4. シート名を変更したい場合は SHEET_NAME を編集
 *   5. 関数 buildMandalaChart を選択して「実行」
 *   6. 初回のみ Google の権限承認が必要
 */

const SHEET_NAME = 'マンダラチャート';

const BIG_GOAL = '世界一の消火剤メーカーになる';

// 8 つのテーマ (中央ブロックの周囲・各外周ブロックの中心)
const THEMES = {
  NW: '製品・技術開発力',
  N : '品質・安全性',
  NE: '国際認証・規格',
  W : 'グローバル販売網',
  E : 'ブランド・マーケティング',
  SW: '人材・組織',
  S : 'サステナビリティ・ESG',
  SE: '経営基盤・財務'
};

// 各テーマに対する 8 個の具体的アクション
// 並び順: [TL, T, TR, L, R, BL, B, BR] (テーマセルを中心とした周囲 8 マス)
const ACTIONS = {
  NW: [ // 製品・技術開発力
    '次世代消火剤の基礎研究',
    'リチウム電池火災用消火剤',
    'AI/IoT連動消火システム',
    '大学・研究機関との共同研究',
    '年間特許出願5件以上',
    '独自ノズル・容器設計',
    '試験設備への継続投資',
    'R&D予算を売上の10%'
  ],
  N: [ // 品質・安全性
    'ISO 9001の高度運用',
    '第三者機関による性能検証',
    '全ロット トレーサビリティ',
    '製造工程の自動化',
    '出荷前100%検査',
    'クレーム率0.1%以下',
    '環境負荷物質の全廃',
    '保管・物流の品質管理'
  ],
  NE: [ // 国際認証・規格
    'UL認証 (米国) 取得',
    'CE/EN規格 (欧州) 取得',
    'GA認証 (中国) 取得',
    'UAE Civil Defence認証',
    'NFPA基準準拠',
    'FM Approval取得',
    'IMO (海事) 規格対応',
    '各国規格動向の継続調査'
  ],
  W: [ // グローバル販売網
    '海外現地法人を5拠点開設',
    '海外代理店100社獲得',
    'Interschutz等の国際展示会出展',
    '多言語Web・カタログ整備',
    '各国消防当局への直接営業',
    'グローバル アフターサービス網',
    '越境ECチャネル構築',
    '現地パートナーの育成'
  ],
  E: [ // ブランド・マーケティング
    '「Fitech」ブランドの世界統一',
    'グローバルWebサイト刷新',
    '実演動画コンテンツの強化',
    '多言語SNS発信',
    '国際メディアでの露出',
    '業界誌への技術寄稿',
    'グッドデザイン等の受賞',
    '顧客事例・実績集の発信'
  ],
  SW: [ // 人材・組織
    '海外人材の積極採用',
    '全社員 語学研修制度',
    '技術者の海外派遣',
    '評価・報酬制度の刷新',
    '幹部・後継者育成プログラム',
    'ダイバーシティ推進',
    '社員数を3倍に拡大',
    '経営理念の全社浸透'
  ],
  S: [ // サステナビリティ・ESG
    'フッ素フリー消火剤の開発',
    'カーボンニュートラル工場化',
    'SDGs宣言の確実な実行',
    '容器・包材のリサイクル設計',
    'フォレストディフェンダー拡販',
    '防災教育CSR活動',
    'ESGレポート発行',
    '災害支援・寄贈活動'
  ],
  SE: [ // 経営基盤・財務
    '年商100億円達成',
    '営業利益率15%以上',
    '自己資本比率50%以上',
    '中期設備投資計画策定',
    'IPO (株式公開) 検討',
    'M&A戦略の推進',
    'BCP (事業継続計画) 整備',
    '基幹システムDX投資'
  ]
};

// 9x9 のテーマ配色 (中心ブロックとそれに対応する外周ブロックを同色)
const COLORS = {
  GOAL : '#fff2cc',
  NW   : '#fce5cd',
  N    : '#d9ead3',
  NE   : '#cfe2f3',
  W    : '#f4cccc',
  E    : '#d9d2e9',
  SW   : '#ead1dc',
  S    : '#fff2cc',
  SE   : '#c9daf8'
};

function buildMandalaChart() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (sheet) {
    sheet.clear();
  } else {
    sheet = ss.insertSheet(SHEET_NAME);
  }

  // 9x9 の値マトリクスを構築 (rows[0..8][0..8])
  const rows = Array.from({length: 9}, () => Array(9).fill(''));

  // 中心ブロック (rows 4-6, cols 4-6 → 0-index で 3-5, 3-5)
  rows[3][3] = THEMES.NW;
  rows[3][4] = THEMES.N;
  rows[3][5] = THEMES.NE;
  rows[4][3] = THEMES.W;
  rows[4][4] = BIG_GOAL;
  rows[4][5] = THEMES.E;
  rows[5][3] = THEMES.SW;
  rows[5][4] = THEMES.S;
  rows[5][5] = THEMES.SE;

  // 外周 8 ブロック - 各ブロックの中心にテーマ、周囲 8 マスにアクション
  // ブロック中心の (row,col) と対応するテーマ key
  const outerCenters = {
    NW: [1, 1],
    N : [1, 4],
    NE: [1, 7],
    W : [4, 1],
    E : [4, 7],
    SW: [7, 1],
    S : [7, 4],
    SE: [7, 7]
  };

  // 周囲 8 マスのオフセット (TL,T,TR,L,R,BL,B,BR)
  const offsets = [
    [-1,-1], [-1,0], [-1,1],
    [ 0,-1],         [ 0,1],
    [ 1,-1], [ 1,0], [ 1,1]
  ];

  Object.keys(outerCenters).forEach(function(key) {
    const c = outerCenters[key];
    rows[c[0]][c[1]] = THEMES[key];
    const acts = ACTIONS[key];
    offsets.forEach(function(off, i) {
      rows[c[0] + off[0]][c[1] + off[1]] = acts[i];
    });
  });

  // 一括書き込み
  const range = sheet.getRange(1, 1, 9, 9);
  range.setValues(rows);

  // スタイル設定
  range.setHorizontalAlignment('center')
       .setVerticalAlignment('middle')
       .setWrap(true)
       .setFontFamily('Noto Sans JP')
       .setFontSize(10)
       .setBorder(true, true, true, true, true, true,
                  '#666666', SpreadsheetApp.BorderStyle.SOLID);

  // 列幅・行高
  for (let c = 1; c <= 9; c++) sheet.setColumnWidth(c, 140);
  for (let r = 1; r <= 9; r++) sheet.setRowHeight(r, 70);

  // ブロック境界 (太線) - 3x3 区切り
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      const blockRange = sheet.getRange(1 + i * 3, 1 + j * 3, 3, 3);
      blockRange.setBorder(true, true, true, true, null, null,
                           '#000000', SpreadsheetApp.BorderStyle.SOLID_THICK);
    }
  }

  // 色付け: 中央セル (大目標)
  sheet.getRange(5, 5).setBackground(COLORS.GOAL)
       .setFontWeight('bold').setFontSize(12);

  // 中央ブロックの 8 テーマ + 対応する外周ブロックの中心セル + 外周ブロック全体に薄色
  const blockMap = {
    NW: { theme:[4,4], outerCenter:[2,2], outerBlock:[1,1,3,3] },
    N : { theme:[4,5], outerCenter:[2,5], outerBlock:[1,4,3,3] },
    NE: { theme:[4,6], outerCenter:[2,8], outerBlock:[1,7,3,3] },
    W : { theme:[5,4], outerCenter:[5,2], outerBlock:[4,1,3,3] },
    E : { theme:[5,6], outerCenter:[5,8], outerBlock:[4,7,3,3] },
    SW: { theme:[6,4], outerCenter:[8,2], outerBlock:[7,1,3,3] },
    S : { theme:[6,5], outerCenter:[8,5], outerBlock:[7,4,3,3] },
    SE: { theme:[6,6], outerCenter:[8,8], outerBlock:[7,7,3,3] }
  };

  Object.keys(blockMap).forEach(function(key) {
    const m = blockMap[key];
    const color = COLORS[key];
    sheet.getRange(m.outerBlock[0], m.outerBlock[1], m.outerBlock[2], m.outerBlock[3])
         .setBackground(color);
    sheet.getRange(m.theme[0], m.theme[1])
         .setBackground(color).setFontWeight('bold');
    sheet.getRange(m.outerCenter[0], m.outerCenter[1])
         .setFontWeight('bold');
  });

  // タイトル行を上に挿入
  sheet.insertRowBefore(1);
  sheet.getRange(1, 1, 1, 9).merge()
       .setValue('株式会社ファイテック 代表取締役 林 富徳 / マンダラチャート (オープンウィンドウ64)')
       .setFontWeight('bold')
       .setFontSize(13)
       .setHorizontalAlignment('center')
       .setBackground('#1c4587')
       .setFontColor('#ffffff');
  sheet.setRowHeight(1, 36);

  sheet.setFrozenRows(1);
  SpreadsheetApp.flush();
}
