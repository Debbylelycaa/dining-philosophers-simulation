from flask import Flask, render_template, jsonify, request
import threading, time, random
from enum import Enum
from datetime import datetime

app = Flask(__name__)

class PhilosopherState(Enum):
    THINKING="thinking"; HUNGRY="hungry"; EATING="eating"

class LogSystem:
    def __init__(self, max_logs=200):
        self.logs=[]; self.max_logs=max_logs; self.lock=threading.Lock()
    def add_log(self, msg, pid=None):
        ts=datetime.now().strftime("%H:%M:%S")
        entry=f"[{ts}] Filosof {pid}: {msg}" if pid is not None else f"[{ts}] {msg}"
        with self.lock:
            self.logs.append(entry)
            if len(self.logs)>self.max_logs: self.logs.pop(0)
    def get_logs(self):
        with self.lock: return self.logs.copy()
    def clear(self):
        with self.lock: self.logs=[]

class BaseDiningSolution:
    def __init__(self, n=5):
        self.n=n
        self.states=[PhilosopherState.THINKING for _ in range(n)]
        self.chopsticks=[threading.Lock() for _ in range(n)]
        self.meals=[0 for _ in range(n)]
        self.running=False; self.paused=False; self.threads=[]
        self.speed=1; self.lock=threading.Lock()  
        self.waiting_since=[None]*n; self.wait_times=[0]*n
        self.log=LogSystem()
        self.pause_event = threading.Event()

    def L(self,i): return i
    def R(self,i): return (i+1)%self.n

    def thinking(self,i):
        with self.lock: 
            self.states[i]=PhilosopherState.THINKING
        self.log.add_log("sedang berpikir...", i)
        
        wait=random.uniform(1,3)/self.speed 
        elapsed = 0
        step = 0.1
        
        while elapsed < wait and self.running:
            if self.paused:
                self.pause_event.wait()
            time.sleep(step)
            if not self.paused:
                elapsed += step

    def hungry(self,i):
        with self.lock:
            self.states[i]=PhilosopherState.HUNGRY
            self.waiting_since[i]=time.time()
        self.log.add_log("lapar, mencoba mengambil sumpit...", i)

    def eating(self,i):
        with self.lock:
            self.states[i]=PhilosopherState.EATING
            self.meals[i]+=1
            if self.waiting_since[i]:
                self.wait_times[i]+=time.time()-self.waiting_since[i]
                self.waiting_since[i]=None
        self.log.add_log("sedang menikmati pisang ijo! 🍌", i)
        
        wait=random.uniform(1,2)/self.speed  
        elapsed = 0
        step = 0.1
        
        while elapsed < wait and self.running:
            if self.paused:
                self.pause_event.wait()
            time.sleep(step)
            if not self.paused:
                elapsed += step

    def acquire_chopsticks(self,i): raise NotImplementedError
    def release_chopsticks(self,i): raise NotImplementedError

    def cycle(self,i):
        while self.running:
            self.thinking(i)
            if not self.running: break
            
            while self.paused and self.running:
                self.pause_event.wait(0.1)
            if not self.running: break
            
            self.hungry(i)
            
            while self.paused and self.running:
                self.pause_event.wait(0.1)
            if not self.running: break
            
            self.acquire_chopsticks(i)
            if not self.running: break
            
            self.eating(i)
            self.release_chopsticks(i)

    def start(self, speed=1):
        self.running=True; self.paused=False; 
        self.speed = speed
        self.pause_event.set()
        self.log.clear(); self.log.add_log("Simulasi dimulai!")
        with self.lock:
            self.states=[PhilosopherState.THINKING for _ in range(self.n)]
            self.meals=[0 for _ in range(self.n)]
            self.wait_times=[0 for _ in range(self.n)]
            self.waiting_since=[None for _ in range(self.n)]
        self.threads=[]
        for i in range(self.n):
            t=threading.Thread(target=self.cycle, args=(i,), daemon=True)
            t.start()
            self.threads.append(t)

    def pause(self): 
        self.paused = True
        self.pause_event.clear()
        with self.lock:
            for i in range(self.n):
                if self.states[i] != PhilosopherState.THINKING:
                    self.states[i] = PhilosopherState.THINKING
        time.sleep(0.3)
        self.log.add_log("Simulasi dijeda")

    def resume(self): 
        self.paused = False
        self.pause_event.set()
        time.sleep(0.2)
        self.log.add_log("Simulasi dilanjutkan")

    def stop(self):
        self.running=False; self.paused=False
        self.pause_event.set()
        self.log.add_log("Simulasi dihentikan")
        for t in self.threads: 
            t.join(timeout=1)

    def reset(self):
        self.stop()
        with self.lock:
            self.states=[PhilosopherState.THINKING for _ in range(self.n)]
            self.meals=[0 for _ in range(self.n)]
            self.wait_times=[0 for _ in range(self.n)]
            self.waiting_since=[None for _ in range(self.n)]
        self.log.clear(); self.log.add_log("Simulasi direset")

    def status(self):
        with self.lock:
            return {
                "states":[s.value for s in self.states],
                "meals":self.meals.copy(),
                "running":self.running,
                "paused":self.paused,
                "logs":self.log.get_logs(),
                "speed": self.speed  
            }

class AsymmetricSolution(BaseDiningSolution):
    def acquire_chopsticks(self, i):
        if i % 2 == 1: 
            first = self.L(i); second = self.R(i); txt = "kiri dulu (ganjil)"
        else:       
            first = self.R(i); second = self.L(i); txt = "kanan dulu (genap)"
        self.log.add_log(f"mengambil sumpit {txt}", i)

        while self.running:
            if self.paused:
                self.pause_event.wait()
                continue
                
            self.chopsticks[first].acquire()
            self.log.add_log(f"berhasil mengambil sumpit {first}", i)

            got_second = self.chopsticks[second].acquire(timeout=0.15)
            if got_second:
                self.log.add_log(f"berhasil mengambil sumpit {second}", i)
                return
            else:
                self.chopsticks[first].release()
                self.log.add_log(
                    f"gagal ambil sumpit {second}, lepas {first} & menunggu ulang", i
                )
                backoff_time = random.uniform(0.05, 0.2) / self.speed  
                backoff_elapsed = 0
                while backoff_elapsed < backoff_time and self.running:
                    if self.paused:
                        self.pause_event.wait()
                    else:
                        time.sleep(0.05)
                        backoff_elapsed += 0.05

    def release_chopsticks(self, i):
        if i % 2 == 1:  
            first = self.L(i); second = self.R(i)
        else:        
            first = self.R(i); second = self.L(i)
        self.chopsticks[second].release()
        self.chopsticks[first].release()
        self.log.add_log("meletakkan kedua sumpit", i)

class FourOnlySolution(BaseDiningSolution):
    def __init__(self,n=5):
        super().__init__(n); self.sem=threading.Semaphore(n-1)
    def acquire_chopsticks(self,i):
        self.log.add_log("meminta izin ke pelayan...", i)
        
        while self.running:
            if self.paused:
                self.pause_event.wait()
                continue
            if self.sem.acquire(timeout=0.1):
                self.log.add_log("mendapat izin dari pelayan", i)
                break
        
        l,r=self.L(i),self.R(i)
        
        while self.running:
            if self.paused:
                self.pause_event.wait()
                continue
            self.chopsticks[l].acquire()
            self.log.add_log(f"ambil kiri ({l})",i)
            break
            
        while self.running:
            if self.paused:
                self.pause_event.wait()
                continue
            self.chopsticks[r].acquire()
            self.log.add_log(f"ambil kanan ({r})",i)
            break
            
    def release_chopsticks(self,i):
        l,r=self.L(i),self.R(i); 
        self.chopsticks[r].release(); 
        self.chopsticks[l].release(); 
        self.sem.release()
        self.log.add_log("meletakkan sumpit & kembalikan izin", i)

class TokenPassingSolution(BaseDiningSolution):
    def __init__(self,n=5):
        super().__init__(n); self.token=True; self.tlock=threading.Lock()
    def acquire_chopsticks(self,i):
        self.log.add_log("menunggu token...", i)
        while self.running:
            if self.paused:
                self.pause_event.wait()
                continue
            if not self.paused:
                with self.tlock:
                    if self.token: 
                        self.token=False; 
                        self.log.add_log("mendapat token!", i); 
                        break
            time.sleep(0.05)
            
        l,r=self.L(i),self.R(i)
        
        while self.running:
            if self.paused:
                self.pause_event.wait()
                continue
            self.chopsticks[l].acquire()
            self.log.add_log(f"ambil kiri ({l})",i)
            break
            
        while self.running:
            if self.paused:
                self.pause_event.wait()
                continue
            self.chopsticks[r].acquire()
            self.log.add_log(f"ambil kanan ({r})",i)
            break
            
    def release_chopsticks(self,i):
        l,r=self.L(i),self.R(i); 
        self.chopsticks[r].release(); 
        self.chopsticks[l].release()
        with self.tlock: 
            self.token=True
        self.log.add_log("meletakkan sumpit & mengembalikan token", i)

class Manager:
    def __init__(self):
        self.sol={
            "asymmetric": AsymmetricSolution(),
            "four_only": FourOnlySolution(),
            "token_passing": TokenPassingSolution()
        }
        self.cur="asymmetric"; self.running=False
    
    def start(self, typ="asymmetric", speed=1):
        if self.running: 
            self.stop()
        self.cur=typ; 
        self.sol[typ].start(speed)  
        self.running=True
    
    def pause(self): 
        self.sol[self.cur].pause()
    
    def resume(self): 
        self.sol[self.cur].resume()
    
    def stop(self): 
        self.running=False
        for s in self.sol.values():
            s.stop()
    
    def reset(self): 
        self.running=False
        for s in self.sol.values():
            s.reset()
    
    def status(self):
        st = self.sol[self.cur].status()
        st["solution_type"] = self.cur
        st["running"] = self.running
        return st

mgr = Manager()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_sim():
    data = request.get_json() or {}
    mgr.start(data.get("solution_type", "asymmetric"), data.get("speed", 1))
    return jsonify({"status": "started"})

@app.route("/pause", methods=["POST"])
def pause_sim():
    mgr.pause()
    return jsonify({"status": "paused"})

@app.route("/resume", methods=["POST"])
def resume_sim():
    mgr.resume()
    return jsonify({"status": "resumed"})

@app.route("/reset", methods=["POST"])
def reset_sim():
    mgr.reset()
    return jsonify({"status": "reset"})

@app.route("/status")
def status():
    return jsonify(mgr.status())

if __name__ == "__main__":
    app.run(debug=True)