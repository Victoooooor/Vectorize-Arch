#include <png++/png.hpp>
#include <iostream>
#include <queue>

#define L 50

using namespace std;
typedef pair<int, int> cord;

int main(int argc, char **argv){
    if(argc<2)
	{
		printf("incorrect params, expected: ./.exe <input> <output>\n");
		exit(EXIT_FAILURE);
	}
    //load image
    png::image< png::rgb_pixel > img(argv[1]);
    vector<cord> edges;
    queue<cord> buff;
    bool checked[img.get_height()][img.get_width()] = {0};
    cout<<img.get_height()<<"\t"<<img.get_width()<<endl;
    //get first black pixel
    for (png::uint_32 y = 0; y < img.get_height(); ++y){
        for (png::uint_32 x = 0; x < img.get_width(); ++x){
            if(img[y][x].red < 127){
                buff.push({y,x});
                checked[y][x] = 1;
                break;
            }
            if(!buff.empty())
                break;
        }
    }
    //start square method
    cord temp;
    int sum = 0;
    int n = 2 * L + 1;
    int x,y;
    while(!buff.empty()){
        temp = buff.front();
        buff.pop();
        edges.push_back(temp);
        x = temp.second;
        y = temp.first;
        //cout<<x<<"\t"<<y<<endl;
        for(int i = -L; i <= L; i++){
            if(x-L >= 0){
                if(y+i>=0 && y+i < img.get_height()){
                    if(y+i-1 == 0 || y+i+1 ==img.get_height()){
                        if(img[y+i][x-L].red < 127){
                            if(checked[y+i][x-L]==0){
                                buff.push({y+i,x-L});
                                checked[y+i][x-L]=1;
                            }
                        }
                            
                    }
                    else if(y+i-1 > 0 && y+i+1 < img.get_height()){
                        if((img[y+i][x-L].red < 127) != (img[y+i-1][x-L].red < 127))
                            if(checked[y+i][x-L]==0){
                                buff.push({y+i,x-L});
                                checked[y+i][x-L] = 1;
                            }
                                
                        else if((img[y+i][x-L].red < 127) != (img[y+i+1][x-L].red < 127))
                            if(checked[y+i][x-L]==0){
                                buff.push({y+i,x-L});
                                checked[y+i][x-L] = 1;
                            }
                    }
                }
            }
            if(x+L < img.get_width()){
                if(y+i>=0 && y+i < img.get_height()){
                    if(y+i-1 == 0 || y+i+1 ==img.get_height()){
                        if(img[y+i][x+L].red < 127)
                            if(checked[y+i][x+L]==0){
                                buff.push({y+i,x+L});
                                checked[y+i][x+L] = 1;
                            }
                    }
                    else if(y+i-1 > 0 && y+i+1 < img.get_height()){
                        if((img[y+i][x+L].red < 127) != (img[y+i-1][x+L].red < 127))
                            if(checked[y+i][x+L]==0){
                                buff.push({y+i,x+L});
                                checked[y+i][x+L] = 1;
                            }
                        else if((img[y+i][x+L].red < 127) != (img[y+i+1][x+L].red < 127))
                            if(checked[y+i][x+L]==0){
                                buff.push({y+i,x+L});
                                checked[y+i][x+L] = 1;
                            }
                    }
                }
            }
            if(y-L >= 0){
                if(x+i>=0 && x+i < img.get_width()){
                    if(x+i-1 == 0 || x+i+1 == img.get_width()){
                        if(img[y-L][x+i].red < 127){
                            if(checked[y-L][x+i]==0){
                                buff.push({y-L,x+i});
                                checked[y-L][x+i]=1;
                            }
                        }
                            
                    }
                    else if(x+i-1 > 0 && x+i+1 < img.get_width()){
                        if((img[y-L][x+i].red < 127) != (img[y-L][x+i-1].red < 127))
                            if(checked[y-L][x+i]==0){
                                buff.push({y-L,x+i});
                                checked[y-L][x+i]=1;
                            }
                                
                        else if((img[y-L][x+i].red < 127) != (img[y-L][x+i+1].red < 127))
                            if(checked[y-L][x+i]==0){
                                buff.push({y-L,x+i});
                                checked[y-L][x+i]=1;
                            }
                    }
                }
            }
            if(y+L < img.get_height()){
                if(x+i>=0 && x+i < img.get_width()){
                    if(x+i-1 == 0 || x+i+1 == img.get_width()){
                        if(img[y+L][x+i].red < 127)
                            if(checked[y+L][x+i]==0){
                                buff.push({y+L,x+i});
                                checked[y+L][x+i] = 1;
                            }
                    }
                    else if(x+i-1 > 0 && x+i+1 < img.get_width()){
                        if((img[y+L][x+i].red < 127) != (img[y+L][x+i-1].red < 127))
                            if(checked[y+L][x+i]==0){
                                buff.push({y+L,x+i});
                                checked[y+L][x+i] = 1;
                            }
                        else if((img[y+L][x+i].red < 127) != (img[y+L][x+i+1].red < 127))
                            if(checked[y+L][x+i]==0){
                                buff.push({y+L,x+i});
                                checked[y+L][x+i] = 1;
                            }
                    }
                }
            }
        }
        
    }
    //write to img
    for(auto ite:edges){
        img[ite.first][ite.second] = png::rgb_pixel(254, 0, 0);
    }
    //write to new png
    img.write(argv[2]);
    return 0;
}