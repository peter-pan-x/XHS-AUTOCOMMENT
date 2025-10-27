# -----------------------------------------------------------------------------
# 小红书自动评论脚本 - V5优化版
# 新增功能: 进程管理 + 日志导出 + 评论记录数据库 + 配置文件分离
# 核心技术: undetected-chromedriver + 弹出层适配 + 智能登录检测
# -----------------------------------------------------------------------------
import time
import random
import os
import pickle
import sqlite3
import sys
import platform
import subprocess
from datetime import datetime
from urllib.parse import quote
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException,
    WebDriverException
)

# 导入配置文件
try:
    from config import Config
except ImportError:
    print("✗ 错误: 未找到config.py配置文件!")
    print("请确保config.py与主程序在同一目录下")
    sys.exit(1)

# -----------------------------------------------------------------------------
# 日志管理类
# -----------------------------------------------------------------------------
class Logger:
    """日志管理类 - 同时输出到控制台和文件"""
    def __init__(self, log_file):
        self.log_file = log_file
        self.logs = []
        
    def log(self, message, print_to_console=True):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        
        if print_to_console:
            print(message)
    
    def export(self):
        """导出日志到文件"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(script_dir, self.log_file)
            
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.logs))
            
            print(f"\n✓ 日志已导出到: {log_path}")
            return True
        except Exception as e:
            print(f"\n✗ 日志导出失败: {e}")
            return False

# -----------------------------------------------------------------------------
# 评论记录数据库类
# -----------------------------------------------------------------------------
class CommentDatabase:
    """评论记录数据库 - 使用SQLite记录已评论的笔记"""
    def __init__(self, db_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(script_dir, db_file)
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commented_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id TEXT UNIQUE NOT NULL,
                    note_url TEXT,
                    comment_text TEXT,
                    comment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"✓ 数据库初始化成功: {self.db_path}")
        except Exception as e:
            print(f"✗ 数据库初始化失败: {e}")
    
    def is_commented(self, note_id):
        """检查笔记是否已评论"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM commented_notes WHERE note_id = ?', (note_id,))
            count = cursor.fetchone()[0]
            
            conn.close()
            return count > 0
        except Exception as e:
            print(f"✗ 检查评论记录失败: {e}")
            return False
    
    def add_comment(self, note_id, note_url, comment_text):
        """添加评论记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO commented_notes (note_id, note_url, comment_text)
                VALUES (?, ?, ?)
            ''', (note_id, note_url, comment_text))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"✗ 添加评论记录失败: {e}")
            return False
    
    def get_stats(self):
        """获取统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM commented_notes')
            total = cursor.fetchone()[0]
            
            conn.close()
            return total
        except Exception as e:
            print(f"✗ 获取统计信息失败: {e}")
            return 0

# -----------------------------------------------------------------------------
# 进程管理函数
# -----------------------------------------------------------------------------
def kill_chrome_processes():
    """杀死所有Chrome/Google相关进程"""
    try:
        system = platform.system()
        print("\n正在清理Chrome/Google相关进程...")
        
        if system == "Windows":
            # Windows系统
            processes = [
                "chrome.exe",
                "chromedriver.exe",
                "GoogleUpdate.exe",
                "GoogleCrashHandler.exe",
                "GoogleCrashHandler64.exe"
            ]
            
            for process in processes:
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/IM", process, "/T"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=5
                    )
                except:
                    pass
        
        elif system == "Linux" or system == "Darwin":
            # Linux/Mac系统
            processes = [
                "chrome",
                "chromium",
                "chromedriver",
                "google-chrome"
            ]
            
            for process in processes:
                try:
                    subprocess.run(
                        ["pkill", "-9", process],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=5
                    )
                except:
                    pass
        
        time.sleep(2)
        print("✓ Chrome进程清理完成")
        return True
        
    except Exception as e:
        print(f"⚠ 进程清理出现异常: {e}")
        return False

# -----------------------------------------------------------------------------
# 辅助函数
# -----------------------------------------------------------------------------
def random_sleep(min_sec=1, max_sec=3):
    """随机延迟"""
    time.sleep(random.uniform(min_sec, max_sec))

def smooth_scroll(driver, ratio=0.6):
    """平滑滚动"""
    try:
        current = driver.execute_script("return window.pageYOffset;")
        target = driver.execute_script(f"return document.body.scrollHeight * {ratio};")
        
        steps = 10
        step_size = (target - current) / steps
        
        for i in range(steps):
            new_pos = current + step_size * (i + 1)
            driver.execute_script(f"window.scrollTo(0, {new_pos});")
            time.sleep(0.05)
    except:
        pass

def save_cookies(driver, filepath):
    """保存Cookies"""
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(driver.get_cookies(), f)
        print(f"✓ Cookies已保存到: {filepath}")
    except Exception as e:
        print(f"✗ 保存Cookies失败: {e}")

def load_cookies(driver, filepath):
    """加载Cookies"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
            print(f"✓ Cookies已加载")
            return True
    except Exception as e:
        print(f"✗ 加载Cookies失败: {e}")
    return False

def check_login_status(driver):
    """检查登录状态(增强版)"""
    try:
        time.sleep(2)
        
        login_indicators = [
            "//button[contains(text(),'登录')]",
            "//div[contains(text(),'扫码登录')]",
            "//span[contains(text(),'扫码登录')]",
            "//div[contains(@class,'login')]",
            ".login-btn",
            ".login-box"
        ]
        
        for selector in login_indicators:
            try:
                if selector.startswith("//"):
                    elem = driver.find_element(By.XPATH, selector)
                else:
                    elem = driver.find_element(By.CSS_SELECTOR, selector)
                
                if elem and elem.is_displayed():
                    return False
            except:
                continue
        
        logged_in_indicators = [
            "a[href='/user/profile/me']",
            "a[href*='/user/profile']",
            ".user-info",
            ".avatar-container",
            "img[alt*='头像']",
            ".user-avatar"
        ]
        
        for selector in logged_in_indicators:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                if elem and elem.is_displayed():
                    return True
            except:
                continue
        
        page_source = driver.page_source
        
        if "扫码登录" in page_source or "手机号登录" in page_source:
            return False
        
        if "个人主页" in page_source or "我的主页" in page_source:
            return True
        
        return False
        
    except Exception as e:
        print(f"\n⚠ 登录状态检查异常: {e}")
        return False

def check_risk_control(driver):
    """检测风控"""
    try:
        risk_keywords = Config.RISK_KEYWORDS
        
        for keyword in risk_keywords:
            xpath = f"//*[contains(text(),'{keyword}')]"
            elements = driver.find_elements(By.XPATH, xpath)
            if elements:
                print(f"✗ 检测到风控: {keyword}")
                return True
        
        return False
    except:
        return False

def extract_note_id(url):
    """从URL中提取笔记ID"""
    try:
        if '/explore/' in url:
            return url.split('/explore/')[-1].split('?')[0]
        elif '/search_result/' in url:
            return url.split('/search_result/')[-1].split('?')[0]
        return None
    except:
        return None
# -----------------------------------------------------------------------------
# 主类
# -----------------------------------------------------------------------------
class XHSBot:
    def __init__(self):
        self.driver = None
        self.config = Config()
        self.logger = Logger(self.config.LOG_FILE)
        self.db = CommentDatabase(self.config.DATABASE_FILE)
        self.last_comment = None
    
    def init_driver(self):
        """初始化undetected-chromedriver"""
        msg = "\n正在初始化浏览器 (使用 undetected-chromedriver)..."
        self.logger.log(msg)
        
        options = uc.ChromeOptions()
        
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        profile_path = os.path.join(desktop_path, self.config.PROFILE_DIR_NAME)
        
        options.add_argument("--disable-blink-features=AutomationControlled")
        if self.config.DISABLE_BOOKMARKS:
            options.add_argument("--disable-features=Bookmarks")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        driver_path = os.path.join(script_dir, "chromedriver.exe")
        
        if not os.path.exists(driver_path):
            msg = f"\n✗ 未找到ChromeDriver: {driver_path}"
            self.logger.log(msg)
            return None
        
        try:
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=driver_path,
                user_data_dir=profile_path,
                use_subprocess=True,
                version_main=141
            )
            
            self.driver.maximize_window()
            self.logger.log("✓ 浏览器初始化成功 (undetected模式)")
            return self.driver
            
        except Exception as e:
            self.logger.log(f"✗ 初始化失败: {e}")
            return None
    
    def search_keyword(self, keyword):
        """搜索关键词"""
        try:
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword )}"
            self.logger.log(f"\n正在搜索: '{keyword}'")
            self.logger.log(f"URL: {search_url}")
            
            self.driver.get(search_url)
            random_sleep(*self.config.SEARCH_INTERVAL)
            
            self.logger.log("✓ 搜索完成")
            return True
            
        except Exception as e:
            self.logger.log(f"✗ 搜索失败: {e}")
            return False
    
    def get_note_links(self):
        """获取笔记链接列表"""
        try:
            selectors = [
                "a.cover",
                ".note-item a",
                ".feeds-page a"
            ]
            
            all_links = []
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for elem in elements:
                        try:
                            if not elem.is_displayed():
                                continue
                            
                            href = elem.get_attribute('href')
                            if not href:
                                continue
                            
                            if ('/explore/' in href or '/search_result/' in href) and len(href) > 50:
                                location = elem.location
                                if location['y'] > self.config.MIN_NOTE_POSITION_Y:
                                    all_links.append({
                                        'element': elem,
                                        'url': href
                                    })
                        except:
                            continue
                except:
                    continue
            
            unique_links = []
            seen_urls = set()
            for link in all_links:
                url = link['url']
                note_id = extract_note_id(url)
                
                if note_id and note_id not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(note_id)
            
            self.logger.log(f"✓ 找到 {len(unique_links)} 个有效笔记")
            return unique_links
            
        except Exception as e:
            self.logger.log(f"✗ 获取笔记列表失败: {e}")
            return []
    
    def open_note(self, note_link):
        """打开笔记"""
        try:
            element = note_link['element']
            
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                element
            )
            random_sleep(1, 2)
            
            location = element.location
            if location['y'] < 100:
                self.driver.execute_script("window.scrollBy(0, -150);");
                random_sleep(0.5, 1)
            
            try:
                element.click()
                self.logger.log("✓ 已点击笔记")
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", element)
                self.logger.log("✓ 已点击笔记(JS)")
            except Exception as e:
                self.logger.log(f"✗ 点击失败: {e}")
                return False
            
            random_sleep(3, 5)
            return True
            
        except Exception as e:
            self.logger.log(f"✗ 打开笔记失败: {e}")
            return False
    
    def post_comment(self, comment_text):
        """发布评论"""
        try:
            random_sleep(2, 3)
            random_sleep(*self.config.COMMENT_INTERVAL)
            
            trigger_button = None
            trigger_selectors = [
                ".inner-when-not-active",
                ".not-active",
                "//span[contains(text(),'说点什么')]",
                "//div[contains(@class,'inner-when-not-active')]"
            ]
            
            self.logger.log("正在查找评论框触发按钮...")
            for selector in trigger_selectors:
                try:
                    if selector.startswith("//"):
                        trigger_button = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        trigger_button = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    if trigger_button and trigger_button.is_displayed():
                        self.logger.log(f"✓ 找到触发按钮: {selector}")
                        break
                except:
                    continue
            
            if not trigger_button:
                self.logger.log("✗ 未找到评论框触发按钮")
                return False
            
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    trigger_button
                )
                random_sleep(0.5, 1)
                trigger_button.click()
                self.logger.log("✓ 已点击触发按钮")
            except:
                try:
                    self.driver.execute_script("arguments[0].click();", trigger_button)
                    self.logger.log("✓ 已点击触发按钮(JS)")
                except Exception as e:
                    self.logger.log(f"✗ 点击触发按钮失败: {e}")
                    return False
            
            random_sleep(1, 2)
            
            comment_box = None
            comment_selectors = [
                "#content-textarea",
                "p.content-input[contenteditable='true']",
                "p[contenteditable='true']",
                "[contenteditable='true']"
            ]
            
            self.logger.log("正在查找输入框...")
            for selector in comment_selectors:
                try:
                    comment_box = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if comment_box and comment_box.is_displayed():
                        self.logger.log(f"✓ 找到输入框: {selector}")
                        break
                except:
                    continue
            
            if not comment_box:
                self.logger.log("✗ 未找到输入框")
                return False
            
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                comment_box
            )
            random_sleep(0.5, 1)
            
            comment_box.click()
            random_sleep(0.5, 1)
            
            self.logger.log(f"正在输入评论: '{comment_text}'")
            
            for char in comment_text:
                comment_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            self.logger.log("✓ 评论内容已输入")
            random_sleep(1, 2)
            
            publish_button = None
            button_selectors = [
                ".btn.submit",
                "button.submit",
                "//button[contains(@class,'submit')]",
                "//button[contains(text(), '发送')]",
                "//button[normalize-space()='发送']"
            ]
            
            self.logger.log("正在查找发送按钮...")
            for selector in button_selectors:
                try:
                    if selector.startswith("//"):
                        publish_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        publish_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if publish_button:
                        self.logger.log(f"✓ 找到发送按钮: {selector}")
                        break
                except:
                    continue
            
            if not publish_button:
                self.logger.log("✗ 未找到发送按钮")
                return False
            
            if not publish_button.is_enabled():
                self.logger.log("⚠ 发送按钮被禁用,等待2秒...")
                random_sleep(2, 3)
            
            try:
                publish_button.click()
                self.logger.log("✓ 已点击发送按钮")
            except:
                self.driver.execute_script("arguments[0].click();", publish_button)
                self.logger.log("✓ 已点击发送按钮(JS)")
            
            random_sleep(2, 3)
            self.logger.log(f"✓ 评论成功: '{comment_text}'")
            return True
            
        except Exception as e:
            self.logger.log(f"✗ 评论失败: {type(e).__name__} - {str(e)}")
            return False
    
    def close_note(self):
        """关闭笔记弹出层"""
        try:
            close_selectors = [
                ".close",
                ".close-btn",
                "button.close",
                "//button[contains(@class,'close')]",
                "//div[contains(@class,'close')]",
                "svg[class*='close']",
                "//svg[contains(@class,'close')]"
            ]
            
            for selector in close_selectors:
                try:
                    if selector.startswith("//"):
                        close_btn = self.driver.find_element(By.XPATH, selector)
                    else:
                        close_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if close_btn and close_btn.is_displayed():
                        close_btn.click()
                        self.logger.log("✓ 已关闭笔记弹出层")
                        random_sleep(2, 3)
                        return True
                except:
                    continue
            
            try:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                self.logger.log("✓ 已按ESC关闭弹出层")
                random_sleep(2, 3)
                return True
            except:
                pass
            
            self.logger.log("⚠ 未能关闭弹出层")
            return False
            
        except Exception as e:
            self.logger.log(f"✗ 关闭弹出层失败: {e}")
            return False
    
    def run(self):
        """主运行函数"""
        self.logger.log("\n" + "="*60)
        self.logger.log("小红书自动评论脚本 - V5优化版")
        self.logger.log("="*60)
        self.logger.log("\n核心技术:")
        self.logger.log("- undetected-chromedriver (反检测)")
        self.logger.log("- 弹出层模式适配")
        self.logger.log("- 增强登录状态检测")
        self.logger.log("- contenteditable输入框支持")
        self.logger.log("- 随机评论 + Cookie持久化")
        self.logger.log("- SQLite数据库记录 (避免重复评论)")
        self.logger.log("- 自动日志导出")
        self.logger.log("="*60)
        
        notes_count = self.config.NOTES_TO_COMMENT
        
        self.logger.log(f"\n配置信息:")
        self.logger.log(f"- 搜索关键词: {self.config.SEARCH_KEYWORD}")
        self.logger.log(f"- 评论内容: 随机从 {len(self.config.COMMENTS)} 条中选择(避免连续重复)")
        self.logger.log(f"- 目标数量: {notes_count}")
        self.logger.log(f"- 最小间隔: {self.config.MIN_INTERVAL}秒")
        self.logger.log(f"- 历史评论: {self.db.get_stats()} 条")
        self.logger.log("\n" + "="*60)
        self.logger.log("\n开始执行...")
        self.logger.log("="*60)
        
        if not self.init_driver():
            return
        
        try:
            self.logger.log("\n正在打开小红书...")
            self.driver.get("https://www.xiaohongshu.com" )
            random_sleep(3, 5)
            
            cookie_loaded = load_cookies(self.driver, self.config.COOKIE_FILE)
            if cookie_loaded:
                self.driver.refresh()
                random_sleep(3, 5)
            
            if not check_login_status(self.driver):
                self.logger.log("\n" + "!"*60)
                self.logger.log(f"未检测到登录状态,请在【{self.config.PREHEAT_TIMEOUT}秒】内:")
                self.logger.log("1. 扫码登录")
                self.logger.log("2. 随意浏览几个笔记")
                self.logger.log("!"*60)
                
                for remaining in range(self.config.PREHEAT_TIMEOUT, 0, -1):
                    print(f"\r剩余时间: {remaining}秒  ", end='', flush=True)
                    time.sleep(1)
                self.logger.log("\n✓ 预热完成", print_to_console=False)
                print("\n✓ 预热完成")
                
                save_cookies(self.driver, self.config.COOKIE_FILE)
            else:
                self.logger.log("✓ 已登录")
            
            if not self.search_keyword(self.config.SEARCH_KEYWORD):
                return
            
            processed = 0
            success = 0
            failed_list = []
            skipped_list = []
            
            while processed < notes_count:
                start_time = time.time()
                
                self.logger.log(f"\n{'='*60}")
                self.logger.log(f"正在处理第 {processed + 1}/{notes_count} 个笔记")
                self.logger.log(f"{'='*60}")
                
                try:
                    notes = self.get_note_links()
                    
                    if not notes or processed >= len(notes):
                        self.logger.log("没有更多笔记,尝试滚动...")
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        random_sleep(3, 5)
                        notes = self.get_note_links()
                        
                        if not notes or processed >= len(notes):
                            self.logger.log("✗ 未找到更多笔记")
                            break
                    
                    note = notes[processed]
                    note_url = note['url']
                    note_id = extract_note_id(note_url)
                    
                    self.logger.log(f"笔记链接: {note_url}")
                    self.logger.log(f"笔记ID: {note_id}")
                    
                    if note_id and self.db.is_commented(note_id):
                        self.logger.log("⚠ 该笔记已评论过,跳过")
                        skipped_list.append(note_url)
                        processed += 1
                        continue
                    
                    if not self.open_note(note):
                        self.logger.log("✗ 无法打开笔记")
                        failed_list.append(note_url)
                        processed += 1
                        continue
                    
                    if check_risk_control(self.driver):
                        self.logger.log("✗ 检测到风控,跳过")
                        failed_list.append(note_url)
                        self.close_note()
                        processed += 1
                        continue
                    
                    self.logger.log("✓ 笔记加载成功")
                    
                    smooth_scroll(self.driver, 0.6)
                    random_sleep(2, 4)
                    
                    available_comments = self.config.COMMENTS.copy()
                    
                    if self.last_comment and self.last_comment in available_comments and len(available_comments) > 1:
                        available_comments.remove(self.last_comment)
                    
                    comment_text = random.choice(available_comments)
                    self.last_comment = comment_text
                    
                    self.logger.log(f"随机选择评论: '{comment_text}'")
                    
                    if self.post_comment(comment_text):
                        success += 1
                        if note_id:
                            self.db.add_comment(note_id, note_url, comment_text)
                            self.logger.log(f"✓ 已记录到数据库")
                    else:
                        failed_list.append(note_url)
                    
                    self.close_note()
                    
                except WebDriverException as e:
                    self.logger.log(f"✗ 浏览器连接错误,脚本终止")
                    break
                except Exception as e:
                    self.logger.log(f"✗ 处理出错: {type(e).__name__}")
                    if 'note' in locals():
                        failed_list.append(note['url'])
                    
                    try:
                        self.close_note()
                    except:
                        pass
                
                processed += 1
                
                if processed < notes_count:
                    elapsed = time.time() - start_time
                    wait_time = max(0, self.config.MIN_INTERVAL - elapsed)
                    
                    if wait_time > 0:
                        msg = f"\n等待 {wait_time:.1f} 秒后继续..."
                        self.logger.log(msg)
                        time.sleep(wait_time)
            
            self.logger.log(f"\n{'='*60}")
            self.logger.log("任务完成!")
            self.logger.log(f"{'='*60}")
            self.logger.log(f"总处理: {processed}")
            self.logger.log(f"成功: {success}")
            self.logger.log(f"跳过(已评论): {len(skipped_list)}")
            self.logger.log(f"失败: {len(failed_list)}")
            
            if skipped_list:
                self.logger.log(f"\n跳过的笔记(已评论过):")
                for url in skipped_list:
                    self.logger.log(f"  - {url}")
            
            if failed_list:
                self.logger.log(f"\n失败的笔记:")
                for url in failed_list:
                    self.logger.log(f"  - {url}")
        
        except Exception as e:
            self.logger.log(f"\n✗ 严重错误: {e}")
            import traceback
            error_trace = traceback.format_exc()
            self.logger.log(error_trace)
        
        finally:
            self.logger.export()
            
            if self.driver:
                print("\n10秒后关闭浏览器...")
                time.sleep(10)
                try:
                    self.driver.quit()
                    print("✓ 浏览器已关闭")
                except:
                    print("浏览器可能已被手动关闭")

# -----------------------------------------------------------------------------
# 主程序入口
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"脚本路径: {os.path.abspath(__file__)}")
    print("-" * 60)
    
    # 1. 杀死所有Chrome进程
    kill_chrome_processes()
    
    # 2. 运行主程序
    bot = XHSBot()
    bot.run()
