// Mock authentication service using localStorage
export const authService = {
  isAuthenticated: () => {
    return localStorage.getItem('porfio_user') !== null;
  },

  login: (email: string, password: string) => {
    // Mock login - in real app, this would call an API
    const user = {
      id: '1',
      email,
      name: email.split('@')[0],
      createdAt: new Date().toISOString(),
    };
    localStorage.setItem('porfio_user', JSON.stringify(user));
    return user;
  },

  register: (email: string, password: string, name: string) => {
    // Mock register - in real app, this would call an API
    const user = {
      id: Math.random().toString(36).substr(2, 9),
      email,
      name,
      createdAt: new Date().toISOString(),
    };
    localStorage.setItem('porfio_user', JSON.stringify(user));
    return user;
  },

  logout: () => {
    localStorage.removeItem('porfio_user');
    localStorage.removeItem('porfio_cv_data');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('porfio_user');
    return userStr ? JSON.parse(userStr) : null;
  },
};

// Mock CV analysis service
export const cvService = {
  uploadCV: (file: File) => {
    // Mock upload - in real app, this would upload to server
    return new Promise((resolve) => {
      setTimeout(() => {
        const cvData = {
          fileName: file.name,
          uploadedAt: new Date().toISOString(),
          size: file.size,
        };
        localStorage.setItem('porfio_cv_data', JSON.stringify(cvData));
        resolve(cvData);
      }, 1500);
    });
  },

  analyzeCV: () => {
    // Mock analysis - in real app, this would call AI API
    return new Promise((resolve) => {
      setTimeout(() => {
        const analysis = {
          overallScore: 78,
          skills: [
            { name: 'JavaScript', level: 85, category: 'Technical' },
            { name: 'React', level: 80, category: 'Technical' },
            { name: 'Node.js', level: 75, category: 'Technical' },
            { name: 'Communication', level: 70, category: 'Soft Skill' },
            { name: 'Leadership', level: 65, category: 'Soft Skill' },
          ],
          recommendations: [
            {
              role: 'Frontend Developer',
              matchScore: 85,
              company: 'Tech Startup',
              location: 'Jakarta',
              salary: 'Rp 12-18 juta/bulan',
              reasons: [
                'Strong React and JavaScript skills',
                'Modern web development experience',
                'Good UI/UX understanding',
              ],
            },
            {
              role: 'Full Stack Developer',
              matchScore: 78,
              company: 'E-commerce Company',
              location: 'Bandung',
              salary: 'Rp 15-22 juta/bulan',
              reasons: [
                'Full stack capabilities with Node.js',
                'Database management experience',
                'API development skills',
              ],
            },
            {
              role: 'Software Engineer',
              matchScore: 72,
              company: 'Financial Services',
              location: 'Surabaya',
              salary: 'Rp 10-15 juta/bulan',
              reasons: [
                'Strong problem-solving skills',
                'Clean code practices',
                'Team collaboration experience',
              ],
            },
          ],
          strengths: [
            'Strong technical foundation in modern web technologies',
            'Proven experience with React ecosystem',
            'Good balance of technical and soft skills',
          ],
          improvements: [
            'Consider expanding backend skills (Python, Java)',
            'Add cloud computing certifications (AWS, Azure)',
            'Develop more leadership experiences',
          ],
          analyzedAt: new Date().toISOString(),
        };
        resolve(analysis);
      }, 3000);
    });
  },

  getStoredCV: () => {
    const cvStr = localStorage.getItem('porfio_cv_data');
    return cvStr ? JSON.parse(cvStr) : null;
  },
};
