from governor import Governor
from urdu_engine import UrduEngine
from api_manager import APIManager

def main():
    gov = Governor()
    api = APIManager()
    engine = UrduEngine()
    
    print("OSCF Software Initialized...")
    # Add your GUI startup or CLI logic here
    
if __name__ == "__main__":
    main()
