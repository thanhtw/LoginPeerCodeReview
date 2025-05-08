"""
Traditional Chinese (zh-tw) translations for Java Peer Review Training System.

This module provides Traditional Chinese translations for the UI and system messages.
"""

# LLM instructions for responding in Traditional Chinese
llm_instructions = """
請用繁體中文回答。使用清晰、簡潔的語言，適合程式設計教育。
以易於理解的方式格式化程式碼範例、錯誤解釋和反饋，以便程式設計學生能夠理解。
"""

# Traditional Chinese (zh-tw) translations
translations = {
    # General
    "app_title": "Java 程式碼審查訓練系統",
    "app_subtitle": "使用 AI 生成的練習來學習和練習 Java 程式碼審查技能",
    
    # Login/Register
    "login": "登入",
    "register": "註冊",
    "email": "電子郵件",
    "password": "密碼",
    "confirm_password": "確認密碼",
    "display_name": "顯示名稱",
    "experience_level": "您的經驗等級",
    "demo_mode": "示範模式",
    "continue_demo": "繼續使用示範模式（無需登入）",
    "login_failed": "登入失敗",
    "invalid_credentials": "無效的電子郵件或密碼",
    "registration_failed": "註冊失敗",
    "fill_all_fields": "請填寫所有欄位",
    "passwords_mismatch": "密碼不符",
    "email_in_use": "電子郵件已被使用",
    "hi": "你好",
    "level": "您的等級",
    "review_times": "審查次數",
    "score": "您的得分",
    "about": "關於",
    "about_app": "此應用程式透過生成具有故意錯誤的程式碼，幫助您學習和練習 Java 程式碼審查技能。",

    #Provide sections
    'llm_provider_setup':'LLM 提供者設定',
    'please_select_LLM':'請選擇您要使用的 LLM 提供者',
    'select_LLM':'選擇 LLM 提供者',
    'select_ollama': 'Ollama 將使用在您本機上運行的本地託管模型',
    'ollama_error':'無法連線到 Ollama：在 http://localhost:11434 連接失敗',
    'use_ollama':'使用 Ollama',
    'connected_ollama':'已連線到 Ollama',
    'groq_api_message':'Groq API 使用雲端託管的模型，並且需要 API 金鑰',
    'groq_api_key':'Groq API 金鑰',
    'test_connection':'測試連線',
    'api_key_required': 'Groq 需要 API 金鑰',
    'connect_groq_success':'已成功連線至 Groq API',
    'connect_groq_failed':'無法連線至 Groq API。請檢查您的 API 金鑰',
    'ollama_mode':'Ollama（本機）',
    'groq_mode':'Groq API（雲端）',
    'change_provider': '變更提供者',
    'provider':'提供者',
    'status':'狀態',
    'using_groq': '使用 Groq API（雲端）',
    'connected_groq':'已連線至 Groq API',
    'connected':'已連線到',


    # Code Generation
    "generate_problem": "生成 Java 程式碼審查問題",
    "error_selection_mode": "錯誤選擇模式",
    "error_selection_prompt": "您想如何選擇錯誤？",
    "advanced_mode": "進階模式：按錯誤類別選擇",
    "specific_mode": "特定模式：選擇確切的錯誤",
    "select_error_categories": "選擇錯誤類別",
    "advanced_mode_help": "進階模式：選擇特定錯誤類別包含在生成的程式碼中。系統將從您選擇的類別中隨機選擇錯誤。",
    "no_categories": "未選擇類別。您必須選擇至少一個類別以生成程式碼。",
    "selected_categories": "已選擇的類別",
    "select_specific_errors": "選擇特定錯誤",
    "error_details": "錯誤詳情",
    "error_categories": "錯誤類別",
    "code_params": "程式碼參數（基於您的等級）",
    "difficulty": "難度",
    "code_length": "程式碼長度",
    "params_based_on_level": "這些參數是根據您的經驗等級自動設定的",
    "generate_code_button": "生成程式碼問題",
    "generating_code": "正在生成和評估程式碼...",
    "code_generation_process": "程式碼生成過程",
    "step1": "1. 生成程式碼",
    "step2": "2. 評估程式碼",
    "step3": "3. 重新生成",
    "step4": "4. 準備審查",
    "generation_stats": "生成統計",
    "quality": "品質",
    "errors_found": "找到的錯誤",
    "generation_attempts": "生成嘗試次數",
    "generate_new": "生成新問題",
    "generated_java_code": "已生成的 Java 程式碼",
    "starting_new_session": "開始新的程式碼審查會話。請配置並生成新問題。",
    "generated_initial_code": "已生成初始程式碼",
    "evaluated_code": "已評估程式碼中的請求錯誤",
    "regenerating_code": "重新生成程式碼",
    "reevaluated_code": "已重新評估生成的程式碼",
    "reevaluating_code": "正在重新評估程式碼...",
    "code_generation_completed": "程式碼生成過程已成功完成",
    "evaluating_code": "正在評估生成的程式碼中的錯誤...",
    "code_generation_complete": "程式碼生成完成！正在進入審查標籤...",
    "workflow_not_initialized": "工作流程狀態未初始化。請刷新頁面。",
    "process_details": "過程詳情",
    "no_process_details": "沒有可用的過程詳情。",
    "code_quality": "程式碼品質",
    "found": "找到",
    "of": "共",
    "requested_errors": "請求的錯誤",
    "improving_code": "改進程式碼品質",
    "all_errors_implemented": "所有請求的錯誤都已成功實現！",
    "good_quality": "生成的良好品質程式碼，錯誤比例為",
    "partial_quality": "生成的程式碼，錯誤比例為",
    "added": "新增了",
    "new_errors": "個新錯誤！",
    "completed": "已完成",
    "attempts": "次嘗試",
    "no_errors_found": "在此類別中未找到錯誤",
    "category": "類別",
    "selected": "已選擇",
    "select": "選擇",
    "remove": "移除",
    "selected_issues": "已選擇的問題",
    "no_specific_issues": "未選擇特定問題。將根據類別使用隨機錯誤。",
    'easy':'簡單的',
    'medium': '中等的',
    'hard':'難的',
    'short':'短的',
    'long':'長的',
    
    # Review
    "review_java_code": "審查 Java 程式碼",
    "no_code_generated": "尚未生成程式碼。請先前往「生成問題」標籤。",
    "submit_review": "提交您的程式碼審查",
    "attempt": "嘗試",
    "of": "共",
    "review_guidelines": "審查指南",
    "how_to_write": "如何撰寫有效的程式碼審查：",
    "be_specific": "具體明確：指出問題發生的確切行或區域",
    "be_comprehensive": "全面：尋找不同類型的問題",
    "be_constructive": "建設性：提出改進建議，而非僅批評",
    "check_for": "檢查：",
    "review_example": "良好審查評論的例子：",
    "enter_review": "在此輸入您的審查評論",
    "submit_review_button": "提交審查",
    "clear": "清除",
    "review_guidance": "審查指導",
    "previous_results": "先前結果",
    "previous_review": "先前審查",
    "processing_review": "正在處理您的審查...",
    "view_feedback": "查看反饋",
    "all_errors_found": "🎉 恭喜！您已找到所有錯誤！前往反饋標籤查看您的結果。",
    "iterations_completed": "您已完成所有 {max_iterations} 次審查迭代。在下一個標籤中查看反饋。",
    
    # Feedback
    "educational_feedback": "教育性反饋：",
    "your_review": "您的審查：",
    "your_final_review": "您的最終審查（嘗試 {iteration}）",
    "issues_found": "找到的問題",
    "accuracy": "準確率",
    "false_positives": "誤報",
    "review_history": "審查歷史",
    "detailed_analysis": "詳細分析",
    "identified_issues": "已識別的問題",
    "missed_issues": "遺漏的問題",
    "new_session": "準備再次審查？",
    "new_session_desc": "開始新的程式碼審查會話以練習不同的錯誤。",
    "start_new_session": "開始新會話",
    "complete_review_first":"請在查看回饋意見前完成所有的審查嘗試",
    "current_process_review1":"目前進度：已完成",
    "current_process_review2":"次嘗試",
    
    # Tabs
    "tab_generate": "1. 生成問題",
    "tab_review": "2. 提交審查",
    "tab_feedback": "3. 查看反饋",
    "tab_logs": "4. LLM 日誌",
    
    # Error categories
    "logical": "邏輯",
    "syntax": "語法",
    "code_quality": "程式碼品質",
    "standard_violation": "標準違規",
    "java_specific": "Java 特有",
    
    # Error category descriptions
    "logical_desc": "程式邏輯、計算和流程控制的問題",
    "syntax_desc": "Java 語言語法和結構錯誤",
    "code_quality_desc": "風格、可讀性和可維護性問題",
    "standard_violation_desc": "違反 Java 慣例和最佳實踐",
    "java_specific_desc": "Java 語言特性的特定問題",
    
    # Language selection
    "language": "語言",
    "english": "英文",
    "chinese": "繁體中文",

    #LLM Log
    "llm_logs_title": "LLM 互動日誌",
    "refresh_logs": "重新整理日誌",
    "logs_to_display": "顯示日誌數量",
    "filter_by_type": "依類型篩選:",
    "filter_by_date": "依日期篩選:",
    "displaying_logs": "顯示 {count} 個最近日誌。最新的日誌最先顯示。",
    "unknown_time": "未知時間",
    "unknown_type": "未知類型",
    "prompt_tab": "提示",
    "response_tab": "回應",
    "metadata_tab": "元數據",
    "prompt_sent": "發送給 LLM 的提示:",
    "response_label": "回應:",
    "no_response": "沒有可用的回應",
    "no_metadata": "沒有可用的元數據",
    "no_logs_match": "沒有日誌符合所選的篩選條件。",
    "no_logs_found": "沒有找到日誌。生成代碼或提交審核以創建日誌條目。",
    "log_info_markdown": """
    ### 日誌信息

    日誌文件存儲在 `llm_logs` 目錄中，其中包含每種互動類型的子目錄：

    - code_generation（代碼生成）
    - code_regeneration（代碼重新生成）
    - code_evaluation（代碼評估）
    - review_analysis（審核分析）
    - summary_generation（摘要生成）

    每個日誌同時存儲為 `.json` 文件（用於程式使用）和 `.txt` 文件（方便閱讀）。
    """,
    "llm_logger_not_initialized": "LLM 日誌記錄器未初始化。",
    "clear_logs": "清除日誌",
    "clear_logs_warning": "這將刪除記憶體中的日誌。磁碟上的日誌文件將被保留。",
    "confirm_clear_logs": "確認清除日誌",
    "logs_cleared": "日誌已清除。"

}