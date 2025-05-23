from datetime import datetime, timedelta
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def store_stock_record(supabase, ticker, name, comment_id=None):
    """Store a stock in the database and update its mention metrics"""
    if not isinstance(ticker, str) or not isinstance(name, str):
        logger.error(f"Invalid ticker or name: {ticker}, {name}")
        return
    now = datetime.now()
    # seven_days_ago = (now - timedelta(days=7)).isoformat()
    print(ticker, name)    
    try:
        existing = supabase.table('stocks')\
            .select('*')\
            .eq('ticker', ticker)\
            .execute()
        
        
        record = {
            'ticker': ticker,
            'name': name,
            'updated_at': now.isoformat(),
            'last_mentioned': now.isoformat()  # This always gets updated
        }

        # If it's a new record
        if not existing.data:
            record.update({
                'created_at': now.isoformat(),
                'mention_count_7d': 1
            })
        

        # Store the record
        supabase.table('stocks').upsert(record).execute()
        
        # Store this mention
        mention_record = {
            'ticker': ticker,
            'mentioned_at': now.isoformat()
        }
        
        # Add comment_id if provided
        if comment_id:
            mention_record['comment_id'] = comment_id
            
        supabase.table('stock_mentions').insert(mention_record).execute()
        
        
    except Exception as e:
        logger.error(f"Error storing stock: {e}")

def get_hot_stocks(supabase, limit=100):
    """Get the most mentioned stocks in the last 7 days"""
    try:
        response = supabase.table('stocks')\
            .select('*')\
            .order('mention_count_7d', desc=True)\
            .limit(limit)\
            .execute()
        data = response.data


        # print(f"data: {data}")
        # sort data by mention_count_7d   
        sorted_data = sorted(data, key=lambda x: x['mention_count_7d'], reverse=True)
        
        orderd_stocks = [stock['ticker'] for stock in sorted_data]
        
        return orderd_stocks

    except Exception as e:
        logger.error(f"Error getting hot stocks: {e}")
        return None