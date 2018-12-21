#Nicholas Mohammad
#11/28/2018
#Raytracer

from PIL import Image
import sys

f = str(sys.argv[1])
file = open(f, "r")
lines = file.readlines()
file.close()

vertices = []
words = lines[0].split(" ")
filename = words[3].strip()

img = Image.new("RGBA", (int(words[1]), int(words[2])), (0,0,0,0))
img.save(filename)
putpixel = img.im.putpixel
width = int(words[1])
height = int(words[2])
eye,forward,right,up = [0,0,0],[0,0,-1],[1,0,0],[0,1,0]
color = [255,255,255,255]
objects = []
lights = []
sphere_count = 0
plane_count = 0
tri_count = 0
bulb_count = 0
vertices = []
fisheye = False

def input(line):
	global plane_count
	global sphere_count
	global tri_count
	global color
	global bulb_count
	global eye
	global forward
	global up
	global right
	global fisheye
	words=[]
	line=(line.strip()).split(" ")
	if len(line) >= 1:
		for word in line:
			if(word!= "" and word!= " "):
				words.append(word)

		if len(words) == 0:
			words.append("")
		if words[0] == "sphere":
			sphere_count+=1
			objects.append(["Sphere" + str(sphere_count),(float(words[1])),(float(words[2])),float(words[3]),float(words[4]),color])
		if words[0] == "sun":
			lights.append([float(words[1]),float(words[2]),float(words[3]),color,"sun"])
		if words[0] == "color":
			color = [int(255*float(words[1])),int(255*float(words[2])),int(255*float(words[3])),255]
		if words[0] == "bulb":
			bulb_count+=1
			lights.append([float(words[1]),float(words[2]),float(words[3]),color,"bulb"+str(bulb_count)])
		if words[0] == "plane":
			plane_count +=1
			objects.append(["Plane" + str(plane_count),float(words[1]),float(words[2]),float(words[3]),float(words[4]),color])
		if words[0] == "eye":
			eye = [float(words[1]),float(words[2]),float(words[3])]
		if words[0] == "xyz":
			vertices.append([float(words[1]),float(words[2]),float(words[3])])
		if words[0] == "trif":
			tri_count += 1
			ind = []
			for word in words:
				if word != "trif":
					word = word if int(word) < 0 else int(word) - 1
					ind.append(word)
			objects.append(["Triangle" + str(tri_count),vertices[int(ind[0])],vertices[int(ind[1])],vertices[int(ind[2])],"",color])
		if words[0] == "forward":
			forward = [float(words[1]),float(words[2]),float(words[3])]
			right = normalize(vec_cross(forward,up))
			up = normalize(vec_cross(right,forward))
		if words[0] == "up":
			up = normalize([float(words[1]),float(words[2]),float(words[3])])
			if round(vec_dot(forward,up),5) !=0:
				D = vec_cross(up,forward)
				up = normalize(vec_cross(forward,D))
			right = normalize(vec_cross(forward,up))
		if words[0] == "fisheye":
			fisheye = True

def raytrace():
	global color
	global forward
	#generate eye, forward, right, and up vectors/points.
	e,f,r,u=list(eye),list(forward),list(right),list(up)
	closest,color,t=sys.maxsize,color,-1
	closest_obj = []
	for x in range(0,width):
		for y in range(0,height):
			closest_obj,closest = [], sys.maxsize
			shoot_ray = True
			forward = f
			#make ray for each pixel
			sx,sy=round((2*x-width)/(max(width,height)),5),round((height-2*y)/max(width,height),5)
			r_sq = 0
			if fisheye:
				sx /= vec_mag(forward)
				sy /= vec_mag(forward)
				r_sq = sx**2 + sy**2
				if round(r_sq**.5,5) > 1:
					continue
				else:
					forward = normalize(forward)
					forward = scal_mult((1-r_sq)**.5,forward)
			r,u=[sx*r[0],sx*r[1],sx*r[2]],[sy*u[0],sy*u[1],sy*u[2]]
			for obj in objects:
				ray_dir = []
				if(obj[0][:6] == "Sphere"):
					ray_dir = normalize(vec_add([forward,r,u]))
					t=Ray_Sphere_Int(obj,ray_dir,eye)
				if(obj[0][:5] == "Plane"):
					ray_dir = normalize(vec_add([forward,r,u]))
					t=Ray_Plane_Int(obj,ray_dir,eye)
				if(obj[0][:8] == "Triangle"):
					ray_dir = normalize(vec_add([forward,r,u]))
					t = Ray_Tri_Int(obj,ray_dir,eye)
				if t >= 0 and t < closest:
					closest=t
					closest_obj = obj

			if closest != sys.maxsize:
				tot_color = [0,0,0,0] if len(lights) != 0 else obj[5]
				#recalculate ray_dir vector:

				ray_dir = normalize(vec_add([forward,r,u]))

				surface_point = [eye[0] + ray_dir[0]*closest,eye[1] + ray_dir[1]*closest,eye[2] + ray_dir[2]*closest]
				obj_color = []
				
				if closest_obj[0][:6]=="Sphere":
					normal = normalize([surface_point[0]-closest_obj[1],surface_point[1]-closest_obj[2],surface_point[2]-closest_obj[3]])
				elif closest_obj[0][:5]=="Plane":
					normal = normalize([closest_obj[1],closest_obj[2],closest_obj[3]])
				elif closest_obj[0][:8]=="Triangle":
					_BA,_CA,_CB = vec_add([closest_obj[2],scal_mult(-1,closest_obj[1])]),vec_add([closest_obj[3],scal_mult(-1,closest_obj[1])]),vec_add([closest_obj[3],scal_mult(-1,closest_obj[2])])
					normal = normalize(vec_cross(_BA,_CA))
				for light in lights:

					if light[-1] == "sun":
						l_dir = normalize([light[0],light[1],light[2]])
						dist =1
						t_light = sys.maxsize
					if light[-1][:4] == "bulb":
						#direction to light from surface point
						l_dir = [-1*surface_point[0]+light[0],-1*surface_point[1]+light[1],-1*surface_point[2]+light[2]]
						dist = vec_mag(l_dir)
						l_dir = normalize(l_dir)
						#need this for bulbs, because if you intersect an object passed the bulb, no need to shadow
						t_light = -1
						for i in range(0,len(l_dir)):
							if light[i] != 0:
								t_light = round(l_dir[i]/light[i],5)
								break

					#check if shadow for each light source
					shadow_int=sys.maxsize
					for obj in objects:
						if obj[0] != closest_obj[0]:
							if(obj[0][:6] == "Sphere"):
								t=Ray_Sphere_Int(obj,l_dir,surface_point)
								if t >= 0 and t > t_light:
									t = -1
							if(obj[0][:5] == "Plane"):
								t=Ray_Plane_Int(obj,l_dir,surface_point)
								if t >= 0 and t > t_light:
									t = -1
							if(obj[0][:8] == "Triangle"):
								t=Ray_Tri_Int(obj,l_dir,surface_point)
								if t >= 0 and t > t_light:
									t = -1
							if t >= 0 and t < closest:
								shadow_int=t
								break

					if vec_dot(normal, [surface_point[0]-eye[0],surface_point[1]-eye[1],surface_point[2]-eye[2]]) > 0:
					 	normal = scal_mult(-1,normal)

					#dot product of unit normal and light direction
					intensity = vec_dot(normal,l_dir)*(1/dist)**2
					if shadow_int != sys.maxsize and shadow_int >0:
						intensity = 0
					#multiply colors together
					l_col = elem_mult(scal_mult(1/255,light[3]),scal_mult(1/255,closest_obj[5]))
					# overall color is sum(intensity*per-object color)
					if intensity > 0:
						tot_color = vec_add([scal_mult(intensity,l_col),tot_color])
						tot_color[3] = 1
					else:
						tot_color = vec_add([tot_color,[0,0,0,1]])

				if len(lights) == 0:
					tot_color = [0,0,0,255]
				else:
					for i in range(0,len(tot_color)):
						tot_color[i] = tot_color[i] if tot_color[i] <= 1 else 1
					tot_color = scal_mult(255,tot_color)
				for i in range(0,len(tot_color)):
					tot_color[i] = int(tot_color[i])

				if shoot_ray:
					putpixel((x,y),tuple(tot_color))
				closest= sys.maxsize
			r,u=right,up
	img.save(filename)
def Ray_Plane_Int(plane,ray_dir,origin):
	normal = normalize([plane[1],plane[2],plane[3]])
	point = []
	dist_normal = vec_dot(ray_dir,normal)
	
	if dist_normal == 0:
		return -1
	#generate point on plane
	if plane[4] == 0:
		point = [0,0,0]
	if plane[1] != 0:
		point = [round(-1*plane[4]/plane[1],5),0,0]
	elif plane[2] != 0:
		point = [0,round(-1*plane[4]/plane[2],5),0]
	elif plane[3] != 0:
		point = [0,0,round(-1*plane[4]/plane[3],5)]

	vec_to_point = [point[0]-origin[0],point[1]-origin[1],point[2]-origin[2]]
	dist = vec_dot(vec_to_point,normal)

	t_c = round(dist/dist_normal,5)

	return t_c
def Ray_Sphere_Int(sphere,ray_dir,origin): #checks to see if ray intersects object, returns t value.
	inside = True if vec_mag([sphere[1]-origin[0],sphere[2]-origin[1],sphere[3]-origin[2]])**2 < sphere[4]**2 else False
	
	t_c = round(vec_dot([sphere[1]-origin[0],sphere[2]-origin[1],sphere[3]-origin[2]],ray_dir),5)

	if not inside and t_c < 0:
		return -1

	ray = vec_add([origin,[t_c*ray_dir[0],t_c*ray_dir[1],t_c*ray_dir[2]]])

	square_dis= round(vec_mag( vec_add([ ray, [-1*sphere[1],-1*sphere[2],-1*sphere[3]] ]) )**2,5)

	if not inside and square_dis > sphere[4]**2:
		return -1

	t_off = round((sphere[4]**2 - square_dis)**.5,5)
	if inside:
		return t_c+t_off
	return t_c-t_off
def Ray_Tri_Int(tri,ray_dir,origin):
	_BA,_CA,_CB = vec_add([tri[2],scal_mult(-1,tri[1])]),vec_add([tri[3],scal_mult(-1,tri[1])]),vec_add([tri[3],scal_mult(-1,tri[2])])
	n = normalize(vec_cross(_BA,_CA))

	_A = vec_add([tri[1]])
	d = vec_dot(tri[1],n)
	if round(vec_dot(ray_dir,n),5) == 0:
		return -1

	t = (vec_dot(n,origin) + d) / vec_dot(ray_dir,n)

	if t < 0:
		return -1

	point = vec_add([origin,scal_mult(t,ray_dir)])

	#tests for if the point is outside of the triangle.
	P_BA = vec_add([point, scal_mult(-1,tri[1])])
	BA = vec_add([_BA,origin])
	test0 = vec_cross(BA,P_BA)
	if vec_dot(n,test0) < 0:
		return -1

	P_CA = vec_add([point,scal_mult(-1,tri[2])])
	CB = vec_add([tri[3],scal_mult(-1,tri[2]),origin])
	test1 = vec_cross(CB,P_CA)
	if vec_dot(n,test1) < 0:
		return -1

	P_CB = vec_add([point,scal_mult(-1,tri[3])])
	AC = vec_add([tri[1],scal_mult(-1,tri[3]),origin])
	test2 = vec_cross(AC,P_CB)
	if vec_dot(n,test2) < 0:
		return -1

	return t

def vec_add(vecs):
	ans=[]
	for i in range(len(vecs[0])):
		ans.append(0)
		for j in range(len(vecs)):
			ans[i] += vecs[j][i]
	return ans
def vec_dot(v1,v2):
	ans = 0
	for i in range(0,len(v1)):
		ans+=(v1[i]*v2[i])
	return ans
def vec_mag(v1):
	mag=0
	for i in v1:
		mag+=(i*i)
	return round(mag**.5,5)
def vec_cross(v1,v2):
	v3 = [v1[1]*v2[2] - v1[2]*v2[1],v1[2]*v2[0] - v1[0]*v2[2],v1[0]*v2[1] - v1[1]*v2[0]]
	return v3
def normalize(v1):
	ans=[]
	mag = vec_mag(v1)

	for i in v1:
		ans.append(round(i/mag,5))
	return ans
def elem_mult(v1,v2):
	ans = []
	if len(v1) != len(v2):
		print("VECTOR SIZES DO NOT MATCH")
		return v1
	for i in range(0,len(v1)):
		ans.append(v1[i]*v2[i])
	return ans
def scal_mult(a,v1):
	ans = []
	for i in v1:
		ans.append(a*i)
	return ans

for line in lines:
	input(line)

raytrace()