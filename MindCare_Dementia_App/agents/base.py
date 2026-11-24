LEVELS=["Easy","Medium","Hard"]
class BaseAgent:
    def recommend(self,current,sessions):
        if len(sessions)<3: return current,"Maintain","Collecting more sessions before changing difficulty."
        recent=sessions[:3]
        avg=sum(float(s["accuracy"]) for s in recent)/3
        completion=sum(bool(s["completed"]) for s in recent)/3
        hints=sum(int(s["hints_used"]) for s in recent)/3
        i=LEVELS.index(current)
        if avg<55 or completion<.67 or hints>=3:
            new=LEVELS[max(0,i-1)]
            return new,("Decrease" if new!=current else "Maintain"),"Recent performance suggests a simpler level may be more comfortable."
        if avg>=85 and completion==1 and hints<=1:
            new=LEVELS[min(2,i+1)]
            return new,("Increase" if new!=current else "Maintain"),"Consistently strong recent performance; offering a small increase."
        return current,"Maintain","Keeping the level stable while progress is observed."
