from sector import get_sector_strength

def sector_rotation_score(stock_sector, hot_sectors):
    if stock_sector in hot_sectors:
        return 1
    return 0.3
