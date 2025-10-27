#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动评论工具 - 图形化配置面板
简单易用的配置界面,无需手动编辑 config.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys

class ConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("小红书自动评论工具 - 配置面板")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # 加载现有配置
        self.load_config()
        
        # 创建界面
        self.create_widgets()
        
    def load_config(self):
        """加载现有配置"""
        try:
            from config import Config
            self.config = Config()
            self.keyword = self.config.SEARCH_KEYWORD
            self.notes_count = self.config.NOTES_TO_COMMENT
            self.interval = self.config.MIN_INTERVAL
            self.comments = self.config.COMMENTS.copy()
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {e}")
            self.keyword = "玉灵膏"
            self.notes_count = 3
            self.interval = 55
            self.comments = ["写得真好", "感谢分享"]
    
    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_frame = tk.Frame(self.root, bg="#4CAF50", height=60)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(
            title_frame, 
            text="小红书自动评论工具 - 配置面板",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # 主容器
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 搜索关键词
        tk.Label(main_frame, text="搜索关键词:", font=("Arial", 11, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.keyword_entry = tk.Entry(main_frame, width=40, font=("Arial", 10))
        self.keyword_entry.insert(0, self.keyword)
        self.keyword_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # 2. 评论数量
        tk.Label(main_frame, text="评论数量:", font=("Arial", 11, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        count_frame = tk.Frame(main_frame)
        count_frame.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
        self.count_var = tk.IntVar(value=self.notes_count)
        self.count_spinbox = tk.Spinbox(
            count_frame, 
            from_=1, 
            to=20, 
            textvariable=self.count_var,
            width=10,
            font=("Arial", 10)
        )
        self.count_spinbox.pack(side=tk.LEFT)
        
        self.count_label = tk.Label(count_frame, text="", fg="gray")
        self.count_label.pack(side=tk.LEFT, padx=10)
        
        # 3. 评论间隔
        tk.Label(main_frame, text="评论间隔 (秒):", font=("Arial", 11, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        interval_frame = tk.Frame(main_frame)
        interval_frame.grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
        
        self.interval_var = tk.IntVar(value=self.interval)
        self.interval_spinbox = tk.Spinbox(
            interval_frame,
            from_=30,
            to=120,
            textvariable=self.interval_var,
            width=10,
            font=("Arial", 10)
        )
        self.interval_spinbox.pack(side=tk.LEFT)
        tk.Label(interval_frame, text="(建议 ≥ 55秒)", fg="gray").pack(side=tk.LEFT, padx=10)
        
        # 注意: 不在这里调用 update_count_label()，因为 risk_label 还没创建
        
        # 4. 评论内容库
        tk.Label(main_frame, text="评论内容库:", font=("Arial", 11, "bold")).grid(
            row=3, column=0, sticky=tk.NW, pady=10
        )
        
        comment_frame = tk.Frame(main_frame)
        comment_frame.grid(row=3, column=1, pady=10, padx=10, sticky=tk.W)
        
        # 评论列表
        self.comment_listbox = tk.Listbox(
            comment_frame,
            width=50,
            height=10,
            font=("Arial", 9),
            selectmode=tk.SINGLE
        )
        self.comment_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        
        scrollbar = tk.Scrollbar(comment_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.comment_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.comment_listbox.yview)
        
        # 注意: 不在这里调用 refresh_comment_list()，因为 comment_count_label 还没创建
        # 先手动加载评论到列表
        for i, comment in enumerate(self.comments, 1):
            self.comment_listbox.insert(tk.END, f"{i}. {comment}")
        
        # 评论管理按钮
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=4, column=1, pady=10, padx=10, sticky=tk.W)
        
        tk.Button(
            btn_frame,
            text="添加评论",
            command=self.add_comment,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9),
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="编辑评论",
            command=self.edit_comment,
            bg="#FF9800",
            fg="white",
            font=("Arial", 9),
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="删除评论",
            command=self.delete_comment,
            bg="#f44336",
            fg="white",
            font=("Arial", 9),
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # 评论数量提示
        self.comment_count_label = tk.Label(
            main_frame,
            text=f"当前评论库共 {len(self.comments)} 条",
            fg="green",
            font=("Arial", 9)
        )
        self.comment_count_label.grid(row=5, column=1, pady=5, padx=10, sticky=tk.W)
        
        # 风险提示
        self.risk_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 10, "bold")
        )
        self.risk_label.grid(row=6, column=0, columnspan=2, pady=10)
        
        # 现在所有组件都创建完成，可以安全调用初始化函数
        self.update_count_label()
        self.update_risk_label()
        
        # 绑定变化监听
        self.count_var.trace("w", lambda *args: self.update_count_label())
        self.interval_var.trace("w", lambda *args: self.update_risk_label())
        
        # 底部按钮
        bottom_frame = tk.Frame(self.root, bg="#f5f5f5", pady=15)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Button(
            bottom_frame,
            text="保存配置并运行",
            command=self.save_and_run,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Button(
            bottom_frame,
            text="仅保存配置",
            command=self.save_only,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11),
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            bottom_frame,
            text="取消",
            command=self.root.quit,
            bg="#9E9E9E",
            fg="white",
            font=("Arial", 11),
            width=10,
            height=2
        ).pack(side=tk.RIGHT, padx=20)
    
    def update_count_label(self):
        """更新评论数量提示"""
        count = self.count_var.get()
        if count <= 5:
            text = "✓ 低风险"
            color = "green"
        elif count <= 8:
            text = "⚠ 中风险"
            color = "orange"
        else:
            text = "✗ 高风险"
            color = "red"
        self.count_label.config(text=text, fg=color)
        self.update_risk_label()
    
    def update_risk_label(self):
        """更新风险提示"""
        count = self.count_var.get()
        interval = self.interval_var.get()
        
        if count <= 5 and interval >= 55:
            text = "✓ 当前配置: 低风险 (推荐)"
            color = "green"
        elif count <= 8 and interval >= 45:
            text = "⚠ 当前配置: 中风险 (谨慎使用)"
            color = "orange"
        else:
            text = "✗ 当前配置: 高风险 (不建议)"
            color = "red"
        
        self.risk_label.config(text=text, fg=color)
    
    def refresh_comment_list(self):
        """刷新评论列表"""
        self.comment_listbox.delete(0, tk.END)
        for i, comment in enumerate(self.comments, 1):
            self.comment_listbox.insert(tk.END, f"{i}. {comment}")
        # 只有当 comment_count_label 存在时才更新
        if hasattr(self, 'comment_count_label'):
            self.comment_count_label.config(text=f"当前评论库共 {len(self.comments)} 条")
    
    def add_comment(self):
        """添加评论"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加评论")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="请输入评论内容:", font=("Arial", 10)).pack(pady=10)
        
        entry = tk.Entry(dialog, width=50, font=("Arial", 10))
        entry.pack(pady=10)
        entry.focus()
        
        def confirm():
            comment = entry.get().strip()
            if not comment:
                messagebox.showwarning("警告", "评论内容不能为空!")
                return
            if comment in self.comments:
                messagebox.showwarning("警告", "该评论已存在!")
                return
            self.comments.append(comment)
            self.refresh_comment_list()
            dialog.destroy()
        
        tk.Button(
            dialog,
            text="确定",
            command=confirm,
            bg="#4CAF50",
            fg="white",
            width=10
        ).pack(side=tk.LEFT, padx=80, pady=10)
        
        tk.Button(
            dialog,
            text="取消",
            command=dialog.destroy,
            bg="#9E9E9E",
            fg="white",
            width=10
        ).pack(side=tk.RIGHT, padx=80, pady=10)
        
        entry.bind("<Return>", lambda e: confirm())
    
    def edit_comment(self):
        """编辑评论"""
        selection = self.comment_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的评论!")
            return
        
        index = selection[0]
        old_comment = self.comments[index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑评论")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="请修改评论内容:", font=("Arial", 10)).pack(pady=10)
        
        entry = tk.Entry(dialog, width=50, font=("Arial", 10))
        entry.insert(0, old_comment)
        entry.pack(pady=10)
        entry.focus()
        entry.select_range(0, tk.END)
        
        def confirm():
            comment = entry.get().strip()
            if not comment:
                messagebox.showwarning("警告", "评论内容不能为空!")
                return
            self.comments[index] = comment
            self.refresh_comment_list()
            dialog.destroy()
        
        tk.Button(
            dialog,
            text="确定",
            command=confirm,
            bg="#4CAF50",
            fg="white",
            width=10
        ).pack(side=tk.LEFT, padx=80, pady=10)
        
        tk.Button(
            dialog,
            text="取消",
            command=dialog.destroy,
            bg="#9E9E9E",
            fg="white",
            width=10
        ).pack(side=tk.RIGHT, padx=80, pady=10)
        
        entry.bind("<Return>", lambda e: confirm())
    
    def delete_comment(self):
        """删除评论"""
        selection = self.comment_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的评论!")
            return
        
        if len(self.comments) <= 1:
            messagebox.showwarning("警告", "至少需要保留一条评论!")
            return
        
        index = selection[0]
        comment = self.comments[index]
        
        if messagebox.askyesno("确认删除", f"确定要删除以下评论吗?\n\n{comment}"):
            self.comments.pop(index)
            self.refresh_comment_list()
    
    def save_config(self):
        """保存配置到 config.py"""
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showerror("错误", "搜索关键词不能为空!")
            return False
        
        if len(self.comments) == 0:
            messagebox.showerror("错误", "评论库不能为空!")
            return False
        
        try:
            # 读取原配置文件
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, "config.py")
            
            # 生成新的配置内容
            config_content = f'''# -----------------------------------------------------------------------------
# 小红书自动评论脚本 - 配置文件
# 此文件由配置面板自动生成,请勿手动编辑
# -----------------------------------------------------------------------------

class Config:
    """配置类 - 所有可配置参数"""
    
    # -------------------------------------------------------------------------
    # 基础配置
    # -------------------------------------------------------------------------
    
    # 搜索关键词
    SEARCH_KEYWORD = "{keyword}"
    
    # 评论内容列表 (脚本会随机选择,避免连续重复)
    COMMENTS = [
'''
            
            # 添加评论列表
            for comment in self.comments:
                # 转义引号
                comment_escaped = comment.replace('"', '\\"')
                config_content += f'        "{comment_escaped}",\n'
            
            config_content += f'''    ]
    
    # 目标评论数量 (默认值,运行时可修改)
    NOTES_TO_COMMENT = {self.count_var.get()}
    
    # -------------------------------------------------------------------------
    # 时间配置
    # -------------------------------------------------------------------------
    
    # 每次评论之间的最小间隔 (秒)
    MIN_INTERVAL = {self.interval_var.get()}
    
    # 搜索后等待时间范围 (秒)
    SEARCH_INTERVAL = (5, 12)
    
    # 评论操作间的延迟 (秒)
    COMMENT_INTERVAL = (3, 6)
    
    # 打字延迟 (秒) - 每个字符之间的延迟
    TYPING_DELAY = (0.1, 0.3)
    
    # 预热时间 (秒) - 等待用户登录和预热的时间
    PREHEAT_TIMEOUT = 55
    
    # -------------------------------------------------------------------------
    # 文件配置
    # -------------------------------------------------------------------------
    
    # Cookie保存文件名
    COOKIE_FILE = "xhs_cookies.pkl"
    
    # 评论记录数据库文件名
    DATABASE_FILE = "xhs_commented_notes.db"
    
    # 日志文件名
    LOG_FILE = "xhs_auto_comment_log.txt"
    
    # -------------------------------------------------------------------------
    # 浏览器配置
    # -------------------------------------------------------------------------
    
    # User-Agent
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.7390.108 Safari/537.36"
    
    # 是否禁用收藏栏 (避免误点击)
    DISABLE_BOOKMARKS = True
    
    # 用户数据目录名称
    PROFILE_DIR_NAME = "AutomationProfile"
    
    # -------------------------------------------------------------------------
    # 风控配置
    # -------------------------------------------------------------------------
    
    # 风控关键词列表
    RISK_KEYWORDS = [
        "操作频繁",
        "异常",
        "验证码",
        "安全验证",
        "请完成验证",
        "当前笔记暂时无法浏览"
    ]
    
    # -------------------------------------------------------------------------
    # 选择器配置
    # -------------------------------------------------------------------------
    
    # 登录状态检测选择器
    LOGIN_SELECTORS = [
        "a[href='/user/profile/me']",
        "a[href*='/user/profile']",
        ".user-info",
        ".avatar",
        "img[alt*='头像']"
    ]
    
    # 笔记链接选择器
    NOTE_SELECTORS = [
        "a[href*='/explore/']",
        "//a[contains(@href,'/explore/')]",
        "//a[@class='cover ld mask']"
    ]
    
    # 评论框选择器
    COMMENT_BOX_SELECTORS = [
        "textarea[placeholder*='评论']",
        "textarea[placeholder*='留下']",
        "textarea.reply-input",
        ".comment-input textarea"
    ]
    
    # 发布按钮选择器
    PUBLISH_BUTTON_SELECTORS = [
        "//button[contains(@class,'submit') and normalize-space()='发布']",
        "//button[normalize-space()='发布']",
        "//button[contains(text(), '发送')]",
        "//div[contains(text(), '发布')]"
    ]
    
    # -------------------------------------------------------------------------
    # 高级配置
    # -------------------------------------------------------------------------
    
    # 最小笔记位置 (像素) - 排除顶部元素,避免点到收藏栏
    MIN_NOTE_POSITION_Y = 100
    
    # 是否启用Cookie持久化
    ENABLE_COOKIE_PERSISTENCE = True
    
    # 是否显示详细日志
    VERBOSE = True
'''
            
            # 写入文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            return True
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
            return False
    
    def save_only(self):
        """仅保存配置"""
        if self.save_config():
            messagebox.showinfo("成功", "配置已保存到 config.py!")
    
    def save_and_run(self):
        """保存配置并运行"""
        if self.save_config():
            messagebox.showinfo("成功", "配置已保存!\n\n即将启动主程序...")
            self.root.destroy()
            
            # 运行主程序
            try:
                import subprocess
                script_dir = os.path.dirname(os.path.abspath(__file__))
                main_script = os.path.join(script_dir, "xiaohongshu_auto_comment_v5.py")
                subprocess.Popen([sys.executable, main_script])
            except Exception as e:
                messagebox.showerror("错误", f"启动主程序失败: {e}")


def main():
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

