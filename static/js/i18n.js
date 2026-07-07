// i18n.js - Language switching system
// Embeds all Chinese-to-English translations

// Translation map (Chinese text -> English text)
const ZH_TO_EN = {
  '财经防护仪表盘': 'Financial Guardian Dashboard',
  '顶部导航': 'Top Navigation',
  '来帮你了': 'here to help',
  '帮你守住钱包': 'Protecting your wallet',
  '当前模式': 'Current Mode',
  '当前模式：': 'Current Mode:',
  '模拟盘': 'Paper Trading',
  '帮助中心': 'Help Center',
  '使用手册': 'User Manual',
  '欢迎来到': 'Welcome to',
  '是你的个人投资助手': 'is your personal investment assistant',
  '帮你盯盘、识套路、算账、做决策。不用懂太多金融术语': 'Tracks market, spots patterns, calculates, helps you decide',
  '一看就明白。': 'Easy to understand.',
  '首页仪表盘': 'Dashboard',
  '你的第一站。打开就能看到': 'Your First Stop',
  '风险红绿灯': 'Risk Traffic Light',
  '当前市场总体风险等级': 'Overall market risk level',
  '实时预警': 'Real-time Alerts',
  '根据行情自动发出的提醒': 'Auto Alerts',
  '对话小窗口': 'Chat Window',
  '右下角卡通小丫头': 'Cartoon character (bottom right)',
  '点它就能问': 'Click to ask AI',
  '套路识别器': 'Pattern Detector',
  '把别人说的话、广告语、': 'Paste sales pitch, ad copy,',
  '的推荐粘贴进去': 'or recommendations here',
  '帮你分析有没有常见套路': 'AI detects common patterns',
  '制造焦虑让你追高': 'Creating FOMO to push prices up',
  '权威背书': 'Authority endorsement',
  '用名人名言、专家头衔压你': 'Using authority to pressure you',
  '限时限量': 'Limited time/quantity',
  '不马上买就亏了': 'Miss out if you wait',
  '稳赚不亏': 'Guaranteed profit',
  '天下哪有这种好事': 'Too good to be true',
  '适用场景': 'Use Cases',
  '微信群公告、直播话术、券商推送、财经博主文章': 'WeChat posts, broker tips, blogger articles',
  '保本计算器': 'Break-even Calculator',
  '算算你的安全边际。输入本金、止损线、止盈线': 'Calculate safety margin. Enter capital, stop-loss, take-profit',
  '告诉你': 'tells you',
  '现在该不该加仓': 'Should You Add Positions',
  '最坏情况亏多少': 'Worst case loss',
  '理想情况赚多少': 'Best Case',
  '当前是安全区还是危险区': 'Safe zone or danger zone',
  '股监控': 'Stock Monitor',
  '黄金白银': 'Gold & Silver',
  '基本金属': 'Base Metals',
  '实时行情看板': 'Live Market Dashboard',
  '覆盖': 'Covers',
  '股主要指数、黄金白银、铜铝锌等大宗商品。每个品种都有': 'Major stock indices, gold/silver, metals. Each has',
  '点评和趋势信号。': 'AI commentary and signals.',
  '回测': 'Backtest',
  '帮你': 'Helps you',
  '防套路检验': 'Stress Test',
  '用历史数据跑一遍交易': 'Simulate using historical data',
  '看看它能不能帮你赚到钱。选个品种': 'See if it makes money. Pick category',
  '选个品种': 'Pick Category',
  '选品种、设本金、选策略': 'Pick category, capital, strategy',
  '选品种': 'Category',
  '初始本金': 'Initial Capital',
  '回看天数': 'Lookback Days',
  '到过去一年': 'Up to 1 year',
  '策略风格': 'Strategy Style',
  '激进': 'Aggressive',
  '激进型': 'Aggressive',
  '稳健': 'Conservative',
  '稳健型': 'Conservative',
  '平衡': 'Balanced',
  '平衡型': 'Balanced',
  '默认': 'Default',
  '自定义': 'Custom',
  '开始回测': 'Start Backtest',
  '用过去一年的真实走势来检验': 'Test against 1 year real data',
  '的预警信号到底准不准。包含': 'Alert accuracy. Includes',
  '历史预警事件时间线': 'Historical alert timeline',
  '命中率统计': 'Hit Rate Stats',
  '的提醒准不准。看看如果听': 'Alert accuracy. See if following',
  '的策略交易': 'strategy trades',
  '看看如果用': 'See if using',
  '的趋势建议': 'trend advice',
  '开始检验': 'Start Test',
  '助手的连接方式。你可以用本地': 'AI connection. Use local',
  '显卡跑': 'GPU',
  '或者外接': 'or external',
  '对话和分析用你自己的模型。': 'Chat uses your model.',
  '本地': 'Local',
  '外接': 'External',
  '地址': 'URL',
  '地址、模型名、': 'URL, model name,',
  '模型名': 'Model',
  '的地址': 'address',
  '里跑的模型名字': 'Model running in',
  '填你本地': 'Enter your local',
  '填外接': 'Enter external',
  '兼容接口': 'Compatible API',
  '保存设置': 'Save Settings',
  '在这里设置': 'Configure here',
  '想切哪个就用哪个。': 'Switch between them.',
  '查股票': 'Search Stocks',
  '查你想看的那只股票': 'Search any stock',
  '帮你分析': 'AI analyzes',
  '输入股票代码或名字': 'Enter code or name',
  '比如': 'e.g.',
  '股核心监控': 'Stock Monitor',
  '帮你盯着市场上最重要的那些股票': 'Watching key stocks',
  '有风吹草动就给你亮灯': 'Lights up when moving',
  '股票名': 'Stock',
  '现价': 'Price',
  '涨跌': 'Change',
  '类型': 'Type',
  '信号灯': 'Signal',
  '大白话': 'Plain Talk',
  '上次更新': 'Updated',
  '刚刚': 'Just now',
  '刷新': 'Refresh',
  '刷新数据': 'Refresh Data',
  '刷新新闻': 'Refresh News',
  '刷新金价': 'Refresh Prices',
  '分析': 'Analyze',
  '市场趋势分析': 'Market Trend Analysis',
  '基于技术指标自动判断大盘走势': 'AI analyzes technical indicators',
  '正在分析趋势': 'Analyzing...',
  '正在分析市场趋势': 'Analyzing market...',
  '帮你盯着最近的财经大事件': 'Tracking financial news',
  '正在抓取新闻': 'Fetching news...',
  '新闻重点': 'News Highlights',
  '帮你解读新闻': 'AI News Analysis',
  '在这里粘贴你看到的消息': 'Paste any message or tip',
  '先贴一点文字进去再检查': 'Paste text to start',
  '输入本金': 'Enter Capital',
  '设个本金': 'Set Capital',
  '亏填负数': 'Loss: negative number',
  '赚填正数': 'Profit: positive number',
  '算一下': 'Calculate',
  '不花真钱的模拟盘': 'Paper trading, no real money',
  '也可以接实盘数据。支持买入': 'Can connect live data. Buy/sell supported',
  '支持买入': 'Buy/sell supported',
  '买入基金': 'Buy Fund',
  '买入弹窗': 'Buy',
  '卖出弹窗': 'Sell',
  '卖出持仓': 'Sell Holdings',
  '买多少股': 'Shares to buy',
  '卖多少股': 'Shares to sell',
  '为什么买': 'Why Buy',
  '为什么卖': 'Why Sell',
  '给自己写个理由': 'Write a reason',
  '确认买入': 'Confirm Buy',
  '确认卖出': 'Confirm Sell',
  '交易记录。': 'Trade History',
  '买卖历史': 'Trade History',
  '买卖建议': 'Buy/Sell Advice',
  '什么时候该跑路': 'When to Run',
  '今天大盘怎么样': 'How is the market today?',
  '助手': 'Assistant',
  '在线': 'Online',
  '正在思考中': 'Thinking...',
  '正在回答': 'Answering...',
  '正在深度分析': 'Analyzing...',
  '正在处理中': 'Processing...',
  '卡了一下': 'Brief Pause',
  '处理中': 'Processing',
  '发个消息': 'Send Message',
  '尽管找我聊': 'Chat Anytime',
  '有什么想问的': 'Ask Anything',
  '风险信号': 'Risk Signals',
  '风险预警': 'Risk Alert',
  '低危': 'Low Risk',
  '高危': 'High Risk',
  '中等': 'Medium',
  '危险': 'Danger',
  '正常状态': 'Normal',
  '正常波动': 'Normal Fluctuation',
  '注意风险': 'Watch Risk',
  '稳当得很': 'Very Safe',
  '涵盖': 'Covers',
  '覆盖大盘、中盘、成长、科技、稳健、海外、行业': 'Large/mid-cap, growth, tech, conservative, overseas, sector',
  '北向资金、主力净流入': 'Northbound Flow',
  '资金流向': 'Capital Flow',
  '市场情绪': 'Sentiment',
  '成交量': 'Volume',
  '成交额': 'Turnover',
  '换手率': 'Turnover Rate',
  '振幅': 'Amplitude',
  '市盈率': 'P/E Ratio',
  '估值': 'Valuation',
  '基本面': 'Fundamentals',
  '均线多头排列': 'MA Bullish',
  '金叉信号已出现': 'Golden Cross',
  '跌到均线了': 'Dropped to MA',
  '感觉要反弹': 'Rebound Expected',
  '金价涨到': 'Gold Up To',
  '金价回调': 'Gold Pullback',
  '金价大涨': 'Gold Surge',
  '黄金就亮灯了': 'Gold Alert On',
  '黄金是老百姓的': 'Gold For The People',
  '我都能用大白话给你解释清楚': 'Explains in plain language',
  '还是看不懂的投资术语': 'Confusing terms',
  '导航': 'Navigation',
  '左右卡通装饰': 'Cartoon decorations',
  '系统公告': 'System Notice',
  '正式上线': 'Official Launch',
  '现在支持模拟盘': 'Now Supports Paper Trading',
  '实盘双模式切换': 'Paper/Live Toggle',
  '市场横着走': 'Market Sideways',
  '市场比较平稳': 'Market Stable',
  '市场有些波动': 'Market Volatile',
  '市场一乱': 'When Market Chaotic',
  '没啥大动静': 'Not Much Happening',
  '有风吹草动就跑': 'Run At First Sign',
  '你投了多少钱': 'How Much Invested',
  '你现在是赚了还是亏了': 'Up or Down',
  '你的': 'Your',
  '你的外接': 'Your External',
  '你的持仓': 'Your Holdings',
  '你的钱现在啥情况': 'How Is Your Money',
  '你设的止损线是多少': 'Your Stop-Loss',
  '你设的止盈线是多少': 'Your Take-Profit',
  '差多少。': 'How Far Off',
  '最坏亏多少': 'Worst Case',
  '能赚多少': 'Potential Profit',
  '亏多少就跑': 'Cut Loss At',
  '赚多少就收': 'Take Profit At',
  '就是亏': 'That Is A Loss',
  '就是赚': 'That Is A Profit',
  '赚到目标了': 'Target Reached',
  '回测结果': 'Backtest Results',
  '还没动手': 'No Trades Yet',
  '赢了几次': 'Wins',
  '总共卖了几次': 'Total Sells',
  '胜率': 'Win Rate',
  '夏普比率': 'Sharpe Ratio',
  '最大回撤': 'Max Drawdown',
  '盈亏比': 'P/L Ratio',
  '成绩单': 'Scorecard',
  '最终资金': 'Final Capital',
  '总收益率': 'Total Return',
  '年化收益': 'Annualized Return',
  '检验出错': 'Test Error',
  '防套路检验报告': 'Test Report',
  '中国宏观': 'China Macro',
  '美国宏观': 'US Macro',
  '加载最新宏观指标': 'Loading Macro Data',
  '宏观数据加载中': 'Macro Loading',
  '正在加载宏观数据': 'Loading Macro',
  '数据暂时没抓到': 'Data Unavailable',
  '影响你钱包的几个大因素': 'Key Factors For Your Wallet',
  '恐慌指数、美元指数、美债收益率等。宏观对了': 'VIX, USD, Treasury Yields',
  '选股就不至于太离谱。': 'Stock Picks Wont Be Off',
  '沪深': 'SH/SZ',
  '中证': 'CSI',
  '纳指': 'Nasdaq',
  '创业板': 'ChiNext',
  '科创': 'STAR',
  '大盘': 'Large Cap',
  '中盘': 'Mid Cap',
  '海外科技': 'Overseas Tech',
  '贵金属': 'Precious Metals',
  '成长': 'Growth',
  '硬科技': 'Hard Tech',
  '板块': 'Sector',
  '没发现什么明显的套路': 'No Obvious Patterns',
  '有点问题': 'Looks Suspicious',
  '大概率中招': 'High Trap Probability',
  '市场概况': 'Market Overview',
  '系统帮你盯着钱包': 'System Watches Wallet',
  '系统正在为你监控': 'System Monitoring',
  '有风吹草动就提醒你': 'Alerts On Movement',
  '有变动会提醒你': 'Alerts On Changes',
  '正在扫描你的持仓': 'Scanning Holdings',
  '实时行情': 'Live Quotes',
  '趋势分析': 'Trend Analysis',
  '趋势分析加载中': 'Trends Loading',
  '趋势分析暂时有点问题': 'Trends Loading',
  '结合新闻': 'Combining News',
  '给你综合建议': 'Comprehensive View',
  '还有哪里没看明白': 'What Else Is Unclear',
  '结合国际形势给你说说': 'Analyze With Global Context',
  '结合大盘、估值、消息面给你说说现在的': 'Analyze With Market, Valuation, News',
  '股到底什么情况': 'Market Situation',
  '股的任何问题': 'Any Stock Questions',
  '现在有什么买卖建议': 'Buy/Sell Advice',
  '算不了': 'Cannot Calculate',
  '仅供参考': 'For Reference Only',
  '历史不代表未来': 'Past Not Future',
  '投资不是赛跑': 'Investing Is Not A Race',
  '先跑完的人不一定跑得最远': 'First Runner Does Not Always Win',
  '投资不是赛跑，先跑完的人不一定跑得最远。': 'Investing Is Not A Race',
  '趋势': 'Trend',
  '穿越': 'Cycle Through',
  '看收益率、胜率、夏普比率、最大回撤': 'Check Return Rate, Win Rate, Sharpe, Max Drawdown',
  '用历史数据做压力测试': 'Stress Test With Historical Data',
  '看看': 'Check',
  '凭感觉的收益对比': 'Feeling-Based Return Comparison',
  '宏观仪表盘': 'Macro Dashboard',
  '全局视角看市场': 'Market Overview',
  '美联储利率、': 'Fed Rate,',
  '、非农': ', NFP',
  '恐慌指数': 'VIX Index',
  '实盘交易': 'Live Trading',
  '卖出': 'Sell',
  '持仓管理': 'Position Management',
  '设置': 'Settings',
  '后端': 'Backend',
  '首页': 'Home',
  '财经新闻': 'Financial News',
  '套路识别': 'Pattern Detection',
  '保本计算': 'Break-even Calc',
  '我的钱包': 'My Wallet',
  '加载中': 'Loading',
  '只主流': 'Only Mainstream',
  '小贴士': 'Tips',
  '先保住本金再谈赚钱': 'Protect Principal First',
  '我盯着的基金': 'Funds I Watch',
  '这些基金系统帮你看著呢': 'System Watches These Funds',
  '基金名': 'Fund Name',
  '状态': 'Status',
  '操作': 'Action',
  '用大白话给你讲讲最近的市场动态': 'Explain Recent Market In Plain Talk',
  '说说看': 'Tell Me',
  '帮你看看现在市场是': 'Check Current Market',
  '还是': 'Or',
  '用大白话给你说清楚': 'Explain In Plain Talk',
  '茅台': 'Moutai',
  '代码': 'Code',
  '帮你看看': 'Check',
  '关于': 'About',
  '茅台现在能买吗': 'Is Moutai A Buy Now',
  '黄金白银行情': 'Gold & Silver Quotes',
  '压箱底宝贝': 'Hidden Gem',
  '品种': 'Category',
  '帮你看看黄金': 'Check Gold',
  '黄金到底是该买还是该卖': 'Buy Or Sell Gold',
  '分析黄金': 'Analyze Gold',
  '关于黄金的任何问题': 'Any Gold Questions',
  '了还是好时机吗': 'Is Still A Good Time',
  '看到什么消息、标题、推送': 'Any Message, Headline, Tip',
  '贴进去': 'Paste Here',
  '帮你看看有没有': 'Check For',
  '开始检查': 'Start Check',
  '试试例子': 'Try Example',
  '就卖': 'Sell',
  '百分比': 'Percentage',
  '重置模拟盘': 'Reset Paper Trading',
  '口袋里的钱': 'Money In Pocket',
  '基金上的钱': 'Money In Fund',
  '总共': 'Total',
  '赚了': 'Profit',
  '亏了': 'Loss',
  '我的持仓': 'My Holdings',
  '钱都在口袋里': 'All Money In Pocket',
  '还没有交易记录': 'No Trades Yet',
  '最后带': 'Last',
  '用的模型名字': 'Model Name Used',
  '点右边可以显示': 'Click Right To Show',
  '隐藏': 'Hide',
  '测试连接': 'Test Connection',
  '模拟回测': 'Simulated Backtest',
  '就出结果。': 'Get Results.',
  '黄金': 'Gold',
  '等更久再买': 'Wait Longer To Buy',
  '早点卖': 'Sell Earlier',
  '不紧不慢': 'Steady',
  '敢于追涨杀跌': 'Dare To Chase And Sell',
  '防套路实战检验': 'Pattern Stress Test',
  '凭感觉追涨杀跌': 'Feeling-Based Chase And Sell',
  '点击': 'Click',
  '先等等': 'Wait First',
  '落袋为安': 'Lock In Profit',
  '再等等': 'Wait More',
  '打开': 'Open',
  '有什么重要财经新闻': 'Any Important Financial News',
  '帮我检查持仓风险': 'Check Position Risk',
  '持仓风险': 'Position Risk',
  '帮我分析这段消息有没有套路': 'Analyze This Message For Patterns',
  '套路分析': 'Pattern Analysis',
  '我是': 'I Am',
  '不管是市场行情、持仓分析': 'Whether Market Or Holdings',
  '遮罩层': 'Overlay'
};

// Detect if a text node contains translatable Chinese text
function hasChinese(text) {
    return /[一-鿿]{2,}/.test(text);
}

// Replace Chinese text with English
function replaceChinese(text) {
    // Sort by length (longest first) to match longer phrases first
    const sortedZh = Object.keys(ZH_TO_EN).sort((a, b) => b.length - a.length);
    
    let result = text;
    for (const zh of sortedZh) {
        const en = ZH_TO_EN[zh];
        // Replace all occurrences
        result = result.split(zh).join(en);
    }
    return result;
}

// Apply English translations to the entire page
function applyEnglish() {
    // Walk all text nodes in the body (excluding script/style tags)
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: function(node) {
                // Skip text inside <script>, <style>, <code>, <pre>
                const parent = node.parentElement;
                if (!parent) return NodeFilter.FILTER_REJECT;
                const tag = parent.tagName.toLowerCase();
                if (['SCRIPT', 'STYLE', 'CODE', 'PRE', 'TITLE'].includes(tag)) {
                    return NodeFilter.FILTER_REJECT;
                }
                if (hasChinese(node.textContent.trim())) {
                    return NodeFilter.FILTER_ACCEPT;
                }
                return NodeFilter.FILTER_REJECT;
            }
        }
    );

    // Collect all text nodes first
    const textNodes = [];
    while (walker.nextNode()) {
        textNodes.push(walker.currentNode);
    }

    // Replace text in each node
    for (const node of textNodes) {
        const original = node.textContent;
        const replaced = replaceChinese(original);
        if (replaced !== original) {
            node.textContent = replaced;
        }
    }

    // Also update placeholders
    document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el => {
        const zh = el.getAttribute('placeholder');
        if (zh && hasChinese(zh)) {
            const en = replaceChinese(zh);
            if (en !== zh) {
                el.setAttribute('placeholder', en);
            }
        }
    });

    // Update page title
    if (hasChinese(document.title)) {
        const newTitle = replaceChinese(document.title);
        document.title = newTitle;
    }

    // Update html lang attribute
    document.documentElement.setAttribute('lang', 'en-US');
}

// Switch language
function switchLang() {
    var btn = document.getElementById('langBtn');
    if (btn && btn.textContent.includes('EN')) {
        // Switch to English
        btn.textContent = '切换';
        applyEnglish();
    } else {
        // Switch back to Chinese - reload page
        location.reload();
    }
}
