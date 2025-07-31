import requests
import json
import os

def test_backend_features():
    """Test the new backend features (NUKE 28-30)"""
    
    # Test 1: Upload video and get analysis
    print("🧪 Testing video upload and analysis...")
    
    with open('test_swing.mp4', 'rb') as f:
        files = {'video': ('test_swing.mp4', f, 'video/mp4')}
        response = requests.post('http://localhost:5000/analyze', files=files)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Video analysis successful!")
        print(f"Video URL: {data.get('video_url')}")
        print(f"Metrics URL: {data.get('metrics_url')}")
        
        # Test 2: Get metrics data
        metrics_response = requests.get(data['metrics_url'])
        if metrics_response.status_code == 200:
            metrics = metrics_response.json()
            print("✅ Metrics retrieved successfully!")
            
            # Test 3: Test PDF Report Generation (NUKE 28)
            print("\n🧪 Testing PDF Report Generation (NUKE 28)...")
            pdf_data = {
                'email': 'test@example.com',
                'metrics': metrics,
                'video_path': data['video_url']
            }
            
            pdf_response = requests.post('http://localhost:5000/send_report', 
                                      json=pdf_data)
            if pdf_response.status_code == 200:
                print("✅ PDF report generation successful!")
            else:
                print(f"❌ PDF report generation failed: {pdf_response.text}")
            
            # Test 4: Test Heatmap Generation (NUKE 29)
            print("\n🧪 Testing Heatmap Generation (NUKE 29)...")
            heatmap_data = {
                'landmark_data': metrics.get('landmark_data', []),
                'video_path': data['video_url']
            }
            
            heatmap_response = requests.post('http://localhost:5000/generate_heatmap', 
                                          json=heatmap_data)
            if heatmap_response.status_code == 200:
                heatmap_result = heatmap_response.json()
                print("✅ Heatmap generation successful!")
                print(f"Heatmap URL: {heatmap_result.get('heatmap_url')}")
            else:
                print(f"❌ Heatmap generation failed: {heatmap_response.text}")
            
            # Test 5: Test Batch Analysis (NUKE 30)
            print("\n🧪 Testing Batch Analysis (NUKE 30)...")
            with open('test_swing.mp4', 'rb') as f1, open('test_swing.mp4', 'rb') as f2:
                files = [
                    ('videos', ('swing1.mp4', f1, 'video/mp4')),
                    ('videos', ('swing2.mp4', f2, 'video/mp4'))
                ]
                batch_response = requests.post('http://localhost:5000/batch_analyze', 
                                            files=files)
            
            if batch_response.status_code == 200:
                batch_result = batch_response.json()
                print("✅ Batch analysis successful!")
                print(f"Total swings analyzed: {batch_result.get('comparison', {}).get('total_swings', 0)}")
            else:
                print(f"❌ Batch analysis failed: {batch_response.text}")
                
        else:
            print(f"❌ Failed to get metrics: {metrics_response.status_code}")
    else:
        print(f"❌ Video analysis failed: {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_backend_features() 